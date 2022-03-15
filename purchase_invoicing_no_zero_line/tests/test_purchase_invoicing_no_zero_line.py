# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, SavepointCase


class TestPurchaseInvoicingNoZeroLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test Journal", "type": "purchase", "code": "TEST", "sequence": 1}
        )
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Account Payable",
                "code": "ACP",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Vendor",
                "is_company": True,
                "property_account_payable_id": cls.account_payable.id,
            }
        )
        cls.account_expense = cls.env["account.account"].create(
            {
                "name": "Account Expense",
                "code": "ACE",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product Test 1",
                "purchase_ok": True,
                "type": "consu",
                "property_account_expense_id": cls.account_expense.id,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product Test 2",
                "purchase_ok": True,
                "type": "consu",
                "property_account_expense_id": cls.account_expense.id,
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "name": cls.product1.name,
                            "product_qty": 5,
                            "price_unit": 100,
                            "product_uom": cls.product1.uom_id.id,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "name": cls.product2.name,
                            "product_qty": 5,
                            "price_unit": 100,
                            "product_uom": cls.product2.uom_id.id,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                ],
            }
        )

    def test_01_all_lines(self):
        self.purchase_order.button_confirm()
        self.purchase_order.order_line[0].qty_received = 5
        view = self.purchase_order.with_context(create_bill=True).action_view_invoice()
        context = view["context"]
        invoice = Form(self.env["account.move"].with_context(context)).save()
        self.assertEqual(len(invoice.invoice_line_ids), 2)

    def test_02_no_zero_lines(self):
        self.journal.avoid_zero_lines = True
        self.purchase_order.button_confirm()
        self.purchase_order.order_line[0].qty_received = 5
        view = self.purchase_order.with_context(create_bill=True).action_view_invoice()
        context = view["context"]
        invoice = Form(self.env["account.move"].with_context(context)).save()
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        view = self.purchase_order.with_context(create_bill=True).action_view_invoice()
        context = view["context"]
        invoice = Form(self.env["account.move"].with_context(context)).save()
        self.assertEqual(len(invoice.invoice_line_ids), 0)
