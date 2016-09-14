# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import SavepointCase


class PurchaseBatchInvoicingCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(PurchaseBatchInvoicingCase, cls).setUpClass()
        cls.account_type1 = cls.env["account.account.type"].create({
            "name": "Account Type 1",
            "type": "payable",
        })
        cls.account1 = cls.env["account.account"].create({
            "name": "Account 1",
            "code": "AC1",
            "user_type_id": cls.account_type1.id,
            "reconcile": True,
        })
        cls.vendor1 = cls.env["res.partner"].create({
            "name": "Vendor 1",
            "supplier": True,
            "is_company": True,
            "property_account_payable_id": cls.account1.id,
        })
        cls.uomcateg1 = cls.env["product.uom.categ"].create({
            "name": "Category 1",
        })
        cls.uom1 = cls.env["product.uom"].create({
            "name": "UOM 1",
            "category_id": cls.uomcateg1.id,
            "factor": 1,
            "active": True,
            "uom_type": "reference",
        })
        cls.product1 = cls.env["product.product"].create({
            "name": "Product 1",
            "purchase_ok": True,
            "type": "product",
            "list_price": 150,
            "standard_price": 100,
            "uom_id": cls.uom1.id,
            "uom_po_id": cls.uom1.id,
            "property_account_expense_id": cls.account1.id,
            "seller_ids": [
                (0, False, {
                    "name": cls.vendor1.id,
                    "min_qty": 1,
                    "price": 100,
                }),
            ],
        })
        cls.po1 = cls.env["purchase.order"].create({
            "partner_id": cls.vendor1.id,
            "order_line": [
                (0, False, {
                    "product_id": cls.product1.id,
                    "name": cls.product1.name,
                    "product_qty": 1,
                    "price_unit": 100,
                    "product_uom": cls.uom1.id,
                    "date_planned": "2016-05-12",
                }),
            ],
        })
        cls.po2 = cls.po1.copy()
        cls.pos = cls.po1 | cls.po2
        for po in cls.pos:
            # Confirm purchase order
            po.button_confirm()
            # Receive products
            cls.env["stock.immediate.transfer"] \
                .with_context(active_id=po.picking_ids.id) \
                .create(dict()).process()
        cls.wizard = cls.env["purchase.batch_invoicing"].with_context(
            active_ids=cls.pos.ids).create(dict())

    def tearDown(self):
        try:
            result = self.wizard.action_batch_invoice()
            self.assertEqual(result["res_model"], "account.invoice")
            invoices = self.env[result["res_model"]].search(result["domain"])
            self.assertEqual(len(invoices), self.expected_invoices)
            self.assertEqual(invoices.mapped("invoice_line_ids.purchase_id"),
                             self.pos)
            self.assertEqual(
                self.expected_untaxed,
                invoices.mapped("amount_untaxed"))
        finally:
            super(PurchaseBatchInvoicingCase, self).tearDown()

    def test_group_po(self):
        """One invoice per purchase order."""
        self.expected_invoices = 2
        self.expected_untaxed = [100, 100]

    def test_group_vendor(self):
        """One invoice per vendor."""
        self.expected_invoices = 1
        self.expected_untaxed = [200]
        self.wizard.grouping = "partner_id"

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
