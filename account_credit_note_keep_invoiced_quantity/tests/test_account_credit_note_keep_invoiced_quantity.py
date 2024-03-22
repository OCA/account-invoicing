# Copyright 2022 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from mock import patch

from odoo.tests import Form, TransactionCase

from odoo.addons.account.models.account_move import AccountMoveLine


class TestAccountCreditNoteKeepInvoicedQuantity(TransactionCase):
    def setUp(self):
        super().setUp()
        partner = self.env.ref("base.res_partner_12")  # Azure Interior
        revenue_account = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        self.invoice = self.env["account.move"].create(
            {
                "journal_id": journal.id,
                "partner_id": partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": revenue_account.id,
                            "name": "Some invoice line",
                            "price_unit": 10,
                            "quantity": 2,
                        },
                    )
                ],
            }
        )
        self.invoice.action_post()
        self.reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.invoice.id,
                active_ids=self.invoice.ids,
                active_model=self.invoice._name,
            )
            .create({"refund_method": "refund"})
        )

    def test_account_credit_note_keep_invoiced_quantity(self):
        """Check that business fields are not propagated."""
        self.reversal.keep_invoiced_quantities = True
        with patch.object(
            AccountMoveLine,
            "_copy_data_extend_business_fields",
        ) as method:
            self.reversal.reverse_moves()
            self.assertTrue(self.invoice.reversal_move_id)
            # The method is not called
            self.assertFalse(method.call_count)

    def test_account_credit_note_reset_invoiced_quantity(self):
        """Check that business fields are propagated.

        In terms of invoiced quantities on order lines, this means that the
        reversal invoice lines are linked to the original invoice's purchase
        and sale order lines, deducting the invoiced quantities.
        """
        self.reversal.keep_invoiced_quantities = False
        with patch.object(
            AccountMoveLine,
            "_copy_data_extend_business_fields",
        ) as method:
            self.reversal.reverse_moves()
            self.assertTrue(self.invoice.reversal_move_id)
            # The method is called once for every invoice move line
            self.assertEqual(method.call_count, 2)

    def test_account_move_reversal_onchange(self):
        """Onchange functionality prevents invalid combinations"""
        form = Form(self.reversal)
        form.refund_method = "modify"
        form.keep_invoiced_quantities = True
        self.assertTrue(form.keep_invoiced_quantities)
        self.assertEqual(form.refund_method, "refund")
        form.refund_method = "modify"
        self.assertEqual(form.refund_method, "modify")
        self.assertFalse(form.keep_invoiced_quantities)
