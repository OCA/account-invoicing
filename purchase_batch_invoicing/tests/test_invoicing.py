# Copyright 2016 Tecnativa - Jairo Llopis
# Copyright 2020 Tecnativa - Sergio Teruel
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest import mock

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase

mock_ns = "odoo.addons.purchase_batch_invoicing.wizards" ".purchase_batch_invoicing"


class PurchaseBatchInvoicingCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(PurchaseBatchInvoicingCase, cls).setUpClass()
        cls.account1 = cls.env["account.account"].create(
            {
                "name": "Account 1",
                "code": "AC1",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.vendor1 = cls.env["res.partner"].create(
            {
                "name": "Vendor 1",
                "is_company": True,
                "property_account_payable_id": cls.account1.id,
            }
        )
        cls.uomcateg1 = cls.env["uom.category"].create({"name": "Category 1"})
        cls.uom1 = cls.env["uom.uom"].create(
            {
                "name": "UOM 1",
                "category_id": cls.uomcateg1.id,
                "factor": 1,
                "active": True,
                "uom_type": "reference",
            }
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "purchase_ok": True,
                "type": "consu",
                "list_price": 150,
                "standard_price": 100,
                "uom_id": cls.uom1.id,
                "uom_po_id": cls.uom1.id,
                "seller_ids": [
                    (0, False, {"name": cls.vendor1.id, "min_qty": 1, "price": 100}),
                ],
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "purchase_ok": True,
                "type": "consu",
                "list_price": 200,
                "standard_price": 50,
                "uom_id": cls.uom1.id,
                "uom_po_id": cls.uom1.id,
                "seller_ids": [
                    (0, False, {"name": cls.vendor1.id, "min_qty": 1, "price": 50}),
                ],
            }
        )
        cls.po1 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor1.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": cls.product1.id,
                            "name": cls.product1.name,
                            "product_qty": 1,
                            "price_unit": 100,
                            "product_uom": cls.uom1.id,
                            "date_planned": "2016-05-12",
                        },
                    ),
                ],
            }
        )
        cls.po2 = cls.po1.copy()
        cls.pos = cls.po1 | cls.po2
        for po in cls.pos:
            # Confirm purchase order
            po.button_confirm()
            # Receive products
            for pl in po.order_line:
                pl.qty_received = pl.product_qty
        cls.wizard = (
            cls.env["purchase.batch_invoicing"]
            .with_context(active_ids=cls.pos.ids)
            .create(dict())
        )

    def check_created_invoices(self, result):
        """The invoices count and sum are OK."""
        self.assertEqual(result["res_model"], "account.move")
        invoices = self.env[result["res_model"]].search(result["domain"])
        self.assertEqual(len(invoices), self.expected_invoices)
        # Regression test for avoiding incorrect journal
        self.assertEqual(invoices[:1].journal_id.type, "purchase")
        self.assertEqual(
            invoices.mapped("invoice_line_ids.purchase_line_id.order_id"), self.pos
        )
        self.assertItemsEqual(self.expected_untaxed, invoices.mapped("amount_untaxed"))

    @mock.patch(mock_ns + "._logger.debug")
    def check_cron(self, grouping, debug):
        """Cron invoices everything, by purchase order."""
        self.assertIn(grouping, {"id", "partner_id"})
        # 1st call to cron should create invoices
        self.wizard.cron_invoice_all_pending(grouping)
        result = debug.call_args[0][1]
        debug.reset_mock()
        self.check_created_invoices(result)
        # 2nd call should create none
        self.wizard.cron_invoice_all_pending()
        debug.assert_called_with("Traceback:", exc_info=True)

    def test_group_po(self):
        """One invoice per purchase order."""
        self.expected_invoices = 2
        self.expected_untaxed = [100, 100]
        self.check_created_invoices(self.wizard.action_batch_invoice())

    def test_group_vendor(self):
        """One invoice per vendor."""
        self.expected_invoices = 1
        self.expected_untaxed = [200]
        self.wizard.grouping = "partner_id"
        self.check_created_invoices(self.wizard.action_batch_invoice())

    def test_draft_order_ignored(self):
        """Draft order is ignored."""
        self.wizard.purchase_order_ids |= self.po1.copy()
        self.test_group_po()

    def test_confirmed_order_without_received_products_ignored(self):
        """Confirmed order without received products gets ignored."""
        po = self.po1.copy()
        po.button_confirm()
        self.wizard.purchase_order_ids |= po
        self.test_group_po()

    def test_all_draft_no_invoice(self):
        """If there are no orders to invoice, an error is raised."""
        self.pos.write({"invoice_status": "no"})
        with self.assertRaises(UserError):
            self.wizard.action_batch_invoice()

    def test_cron_group_po(self):
        """Cron invoices everything, by purchase order."""
        self.expected_invoices = 2
        self.expected_untaxed = [100, 100]
        self.check_cron("id")

    def test_cron_group_vendor(self):
        """Cron invoices everything, by vendor."""
        self.expected_invoices = 1
        self.expected_untaxed = [200]
        self.check_cron("partner_id")

    def test_wizard_creation_without_context(self):
        """Ensure default value for ``purchase_order_ids`` works."""
        self.env["purchase.batch_invoicing"].create({})

    def invoice_line_partial_received(self, exclude_zero_qty=False):
        po3 = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor1.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product1.id,
                            "name": self.product1.name,
                            "product_qty": 1,
                            "price_unit": 100,
                            "product_uom": self.uom1.id,
                            "date_planned": "2016-05-12",
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.product2.id,
                            "name": self.product1.name,
                            "product_qty": 10,
                            "price_unit": 50,
                            "product_uom": self.uom1.id,
                            "date_planned": "2016-05-12",
                        },
                    ),
                ],
            }
        )
        po2 = self.po1.copy()
        self.pos = self.po1 | po2 | po3
        for po in self.pos:
            # Confirm purchase order
            po.button_confirm()
            # Receive products
            for pl in po.order_line.filtered(lambda x: x.product_id == self.product1):
                pl.qty_received = pl.product_qty
        self.wizard = (
            self.env["purchase.batch_invoicing"]
            .with_context(active_ids=self.pos.ids)
            .create(dict())
        )
        self.expected_invoices = 1
        self.expected_lines = 4
        self.expected_untaxed = [300]
        self.wizard.grouping = "partner_id"
        self.wizard.exclude_zero_qty = exclude_zero_qty
        if exclude_zero_qty:
            self.expected_lines = 3
        self.check_created_invoices(self.wizard.action_batch_invoice())

    def test_invoice_line_partial_received_invoice_zero_qty(self):
        self.invoice_line_partial_received()

    def test_invoice_line_partial_received_not_invoice_zero_qty(self):
        self.invoice_line_partial_received(exclude_zero_qty=True)
