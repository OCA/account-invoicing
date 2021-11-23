# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestMoveRefPropagation(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        account_receivable = cls.company_data["default_account_receivable"]
        account_revenue = cls.company_data["default_account_revenue"]
        currency = cls.currency_data["currency"]
        today = date.today()

        cls.move_to_reverse = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "date": today,
                "ref": "TEST REF",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "debit": 1200.0,
                            "credit": 0.0,
                            "amount_currency": 3600.0,
                            "account_id": account_receivable.id,
                            "currency_id": currency.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "debit": 0.0,
                            "credit": 1200.0,
                            "account_id": account_revenue.id,
                        },
                    ),
                ],
            }
        )
        cls.move_to_reverse.action_post()

    def _reverse_move(self, method):
        reverse_wiz_obj = self.env["account.move.reversal"].with_context(
            active_model="account.move", active_ids=self.move_to_reverse.ids
        )
        reverse_wiz = reverse_wiz_obj.create(
            {
                "date": self.move_to_reverse.date,
                "reason": "no reason",
                "refund_method": method,
            }
        )
        action = reverse_wiz.reverse_moves()
        return self.env["account.move"].browse(action["res_id"])

    def test_reverse_move_propagate_ref(self):
        """Tests that ref is not passed from entry to reversal move"""
        # Reverse the move
        reversal = self._reverse_move(method="cancel")
        # Check that move and reversal move have different ref
        self.assertNotEqual(self.move_to_reverse.ref, reversal.ref)

    def test_new_draft_move_propagate_ref(self):
        """Tests that ref is passed from entry to new draft move"""
        # Reverse the move
        reversal = self._reverse_move(method="modify")
        # Check that move and newly created move have same ref
        self.assertEqual(self.move_to_reverse.ref, reversal.ref)
