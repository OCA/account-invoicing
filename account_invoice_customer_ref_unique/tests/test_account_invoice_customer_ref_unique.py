# Copyright 2016 Acsone
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceCustomerRefUnique(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # ENVIRONMENTS
        cls.account_account = cls.env["account.account"]
        cls.account_move = cls.env["account.move"].with_context(
            **{"tracking_disable": True}
        )

        # INSTANCES
        cls.partner = cls.env.ref("base.res_partner_2")
        # Account for invoice
        cls.account = cls.account_account.search(
            [
                (
                    "account_type",
                    "=",
                    "liability_payable",
                )
            ],
            limit=1,
        )
        # Invoice with unique reference 'ABC123'
        cls.invoice = cls.account_move.create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": fields.Date.today(),
                "move_type": "out_invoice",
                "customer_invoice_number": "ABC123",
                "invoice_line_ids": [(0, 0, {"partner_id": cls.partner.id})],
            }
        )

    def test_check_unique_customer_invoice_number_insensitive(self):
        # A new invoice instance with an existing customer_invoice_number
        with self.assertRaises(ValidationError):
            self.account_move.create(
                {
                    "partner_id": self.partner.id,
                    "move_type": "out_invoice",
                    "customer_invoice_number": "ABC123",
                }
            )
        # A new invoice instance with a new customer_invoice_number
        self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "customer_invoice_number": "ABC123bis",
            }
        )

    def test_onchange_customer_invoice_number(self):
        self.invoice._onchange_customer_invoice_number()
        self.assertEqual(
            self.invoice.ref,
            self.invoice.customer_invoice_number,
            "_onchange_customer_invoice_number",
        )

    def test_copy_invoice(self):
        invoice2 = self.invoice.copy()
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(invoice2.ref, "")

    def test_reverse_invoice(self):
        self.invoice._post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "refund_method": "refund",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(refund.ref, "")

    def test_reverse_moves_robustness(self):
        res = self.invoice._reverse_moves()
        self.assertTrue(res.is_sale_document(include_receipts=True))
