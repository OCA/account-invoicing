# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseInvoicingNoZeroLine(TransactionCase):
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
                "account_type": "liability_payable",
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
                "account_type": "expense",
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

    def _create_invoice_from_po_ref(self, po=False):
        if not po:
            po = self.purchase_order
        supplier_form = self.env.ref("account.view_move_form")
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice"),
            view=supplier_form,
        )

        invoice_form.purchase_vendor_bill_id = self.env["purchase.bill.union"].browse(
            -po.id
        )
        invoice = invoice_form.save()
        return invoice

    def test_01_all_lines(self):
        self.purchase_order.button_confirm()
        self.purchase_order.order_line[0].qty_received = 5
        invoice = self._create_invoice_from_po_ref()
        self.assertEqual(len(invoice.invoice_line_ids), 2)

    def test_02_no_zero_lines(self):
        self.journal.avoid_zero_lines = True
        self.purchase_order.button_confirm()
        self.purchase_order.order_line[0].qty_received = 5
        invoice = self._create_invoice_from_po_ref()
        self.assertEqual(len(invoice.invoice_line_ids), 1)
