from odoo import fields

from .common import AccountInvoiceRefundOptionTest


class TestAccountInvoiceRefundOption(AccountInvoiceRefundOptionTest):
    def test_account_invoice_refund_option(self):
        """
        Test the account invoice refund option to refund only selected
        invoice line.
        """
        # Create an invoice
        move = self.env["account.move"].create(
            dict(
                name="Test Customer Invoice",
                invoice_payment_term_id=self.payment_term.id,
                journal_id=self.journalrec.id,
                partner_id=self.partner3.id,
                line_ids=self.move_line_data,
            )
        )

        # Validate an invoice
        move.action_post()

        # Check invoice and invoice line
        assert move and move.line_ids
        # Create refund of selected invoice line
        invoice_refund_wizard = self.account_move_reversal_obj.create(
            [
                {
                    "date": fields.Datetime.today(),
                    "reason": "Test Reason",
                    "filter_refund": True,
                    "move_ids": [(6, 0, [move.id])],
                    "refund_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.env.ref(
                                    "product.product_product_1"
                                ).id,
                                "quantity": 5,
                            },
                        ),
                    ],
                    "journal_id": move.journal_id.id,
                }
            ]
        )

        # Refund invoice
        ctx = {"active_ids": move.ids}
        invoice_refund_wizard.with_context(**ctx).refund_moves()

        # Check refund is created and attached to the same invoice
        assert invoice_refund_wizard.new_move_ids
