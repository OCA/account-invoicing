# Copyright 2016 Acsone
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError

from odoo.addons.account.tests.invoice_test_common import InvoiceTestCommon


class TestAccountInvoiceSupplierRefUnique(InvoiceTestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ENVIRONMENTS
        cls.account_account = cls.env["account.account"]
        cls.account_invoice = cls.env["account.move"].with_context(
            {"tracking_disable": True}
        )

        # INSTANCES
        cls.partner = cls.env.ref("base.res_partner_2")
        # Account for invoice
        cls.account = cls.account_account.search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        # Invoice with unique reference 'ABC123'
        cls.invoice = cls.account_invoice.create(
            {
                "partner_id": cls.partner.id,
                "type": "in_invoice",
                "supplier_invoice_number": "ABC123",
            }
        )

    def test_check_unique_supplier_invoice_number_insensitive(self):
        # A new invoice instance with an existing supplier_invoice_number
        with self.assertRaises(ValidationError):
            self.account_invoice.create(
                {
                    "partner_id": self.partner.id,
                    "type": "in_invoice",
                    "supplier_invoice_number": "ABC123",
                }
            )
        # A new invoice instance with a new supplier_invoice_number
        self.account_invoice.create(
            {
                "partner_id": self.partner.id,
                "type": "in_invoice",
                "supplier_invoice_number": "ABC123bis",
            }
        )

    def test_onchange_supplier_invoice_number(self):
        self.invoice._onchange_supplier_invoice_number()
        self.assertEqual(
            self.invoice.ref,
            self.invoice.supplier_invoice_number,
            "_onchange_supplier_invoice_number",
        )

    def test_copy_invoice(self):
        invoice2 = self.invoice.copy()
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(invoice2.ref, "")

    def test_reverse_invoice(self):
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "refund_method": "refund",
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(refund.ref, "")

    def test_reverse_moves_robustness(self):
        res = self.invoice._reverse_moves()
        self.assertTrue(res.is_purchase_document(include_receipts=True))
