# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import TransactionCase


class TestAccountMoveLineWarehouse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Second Warehouse",
                "code": "WH2",
                "company_id": cls.company.id,
            }
        )

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
                "purchase_method": "purchase",
            }
        )
        cls.account_income = cls.env["account.account"].search(
            [
                ("company_ids", "in", cls.company.ids),
                ("account_type", "=", "income"),
            ],
            limit=1,
        )
        cls.account_expense = cls.env["account.account"].search(
            [
                ("company_ids", "in", cls.company.ids),
                ("account_type", "=", "expense"),
            ],
            limit=1,
        )
        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.purchase_journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.product.categ_id.property_account_income_categ_id = cls.account_income

        # Picking type for second warehouse (for purchase orders)
        cls.picking_type_in_wh2 = cls.env["stock.picking.type"].search(
            [
                ("warehouse_id", "=", cls.warehouse_2.id),
                ("code", "=", "incoming"),
            ],
            limit=1,
        )

    def _create_sale_order(self, warehouse):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        sale.action_confirm()
        return sale

    def _create_purchase_order(self, picking_type):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": picking_type.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 1,
                            "price_unit": 80.0,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        purchase.button_confirm()
        return purchase

    def _invoice_sale(self, sale):
        sale._create_invoices()
        return sale.invoice_ids

    def _invoice_purchase(self, purchase):
        purchase.action_create_invoice()
        return purchase.invoice_ids

    def test_sale_single_warehouse(self):
        sale = self._create_sale_order(self.warehouse)
        invoice = self._invoice_sale(sale)
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda aml: aml.display_type not in ("line_section", "line_note")
        )
        self.assertEqual(len(invoice_line), 1)
        self.assertEqual(invoice_line.warehouse_id, self.warehouse)

    def test_sale_no_sale_line(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.sale_journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Manual line",
                            "product_id": self.product.id,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                        },
                    )
                ],
            }
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertFalse(invoice_line.warehouse_id)

    def test_sale_multiple_warehouses_same_line(self):
        sale_1 = self._create_sale_order(self.warehouse)
        sale_2 = self._create_sale_order(self.warehouse_2)

        # Créer une facture manuelle regroupant les deux SO lines
        so_line_1 = sale_1.order_line[0]
        so_line_2 = sale_2.order_line[0]
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.sale_journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Grouped line",
                            "product_id": self.product.id,
                            "price_unit": 200.0,
                            "account_id": self.account_income.id,
                            "sale_line_ids": [(6, 0, [so_line_1.id, so_line_2.id])],
                        },
                    )
                ],
            }
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertFalse(invoice_line.warehouse_id)

    def test_sale_multiple_lines_same_warehouse(self):
        sale_1 = self._create_sale_order(self.warehouse)
        sale_2 = self._create_sale_order(self.warehouse)

        so_line_1 = sale_1.order_line[0]
        so_line_2 = sale_2.order_line[0]
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.sale_journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Grouped line same warehouse",
                            "product_id": self.product.id,
                            "price_unit": 200.0,
                            "account_id": self.account_income.id,
                            "sale_line_ids": [(6, 0, [so_line_1.id, so_line_2.id])],
                        },
                    )
                ],
            }
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(invoice_line.warehouse_id, self.warehouse)

    def test_sale_warehouse_updated_on_so_change(self):
        sale = self._create_sale_order(self.warehouse)
        invoice = self._invoice_sale(sale)
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda aml: aml.display_type not in ("line_section", "line_note")
        )
        self.assertEqual(invoice_line.warehouse_id, self.warehouse)

        sale.warehouse_id = self.warehouse_2
        self.assertEqual(invoice_line.warehouse_id, self.warehouse_2)

    def test_purchase_single_warehouse(self):
        picking_type_in = self.env["stock.picking.type"].search(
            [
                ("warehouse_id", "=", self.warehouse.id),
                ("code", "=", "incoming"),
            ],
            limit=1,
        )
        purchase = self._create_purchase_order(picking_type_in)
        invoice = self._invoice_purchase(purchase)
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda aml: aml.display_type not in ("line_section", "line_note")
        )
        self.assertTrue(invoice_line)
        self.assertEqual(invoice_line.warehouse_id, self.warehouse)

    def test_purchase_no_purchase_line(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.purchase_journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Manual purchase line",
                            "product_id": self.product.id,
                            "price_unit": 80.0,
                            "account_id": self.account_expense.id,
                        },
                    )
                ],
            }
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertFalse(invoice_line.warehouse_id)
