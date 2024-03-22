#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestRefund(AccountTestInvoicingCommon):
    def test_out_receipt_refund_modify(self):
        """Refund a Customer Receipt and create a new Draft Receipt."""
        # Arrange: Post a Customer Receipt
        out_receipt = self.init_invoice(
            "out_receipt",
            post=True,
            amounts=[
                10.0,
            ],
        )

        # Act: Refund the Receipt
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_model=out_receipt._name,
                active_ids=out_receipt.ids,
            )
            .create(
                {
                    "reason": "Test",
                    "refund_method": "modify",
                }
            )
        )
        move_action = move_reversal.reverse_moves()
        move_model = move_action["res_model"]
        move_id = move_action["res_id"]

        # Assert
        # The new Receipt is in Draft and has the same amount
        # as the original Receipt
        new_move = self.env[move_model].browse(move_id)
        self.assertEqual(new_move.state, "draft")
        self.assertEqual(new_move.move_type, out_receipt.move_type)
        self.assertEqual(new_move.amount_total, out_receipt.amount_total)

        # The Refund Receipt is in Posted and has the opposite amount
        # as the original Receipt, and opposite quantity
        reverse_move = out_receipt.reversal_move_id
        self.assertEqual(reverse_move.state, "posted")
        self.assertEqual(reverse_move.move_type, out_receipt.move_type)
        self.assertEqual(reverse_move.amount_total, -out_receipt.amount_total)
        self.assertEqual(
            reverse_move.invoice_line_ids.quantity,
            -out_receipt.invoice_line_ids.quantity,
        )
