# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestAccountMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountMove = cls.env["account.move"]
        cls.today = fields.Date.context_today(cls.AccountMove)

    def _new_move(self, move_type="out_invoice", invoice_date_due=None):
        return self.AccountMove.new(
            {
                "move_type": move_type,
                "invoice_date_due": invoice_date_due,
            }
        )

    def test_show_overdue_reason_on_overdue_customer_invoice(self):
        move = self._new_move(invoice_date_due=self.today - timedelta(days=1))

        self.assertTrue(move.show_overdue_reason)

    def test_do_not_show_overdue_reason_on_customer_invoice_due_today(self):
        move = self._new_move(invoice_date_due=self.today)

        self.assertFalse(move.show_overdue_reason)

    def test_do_not_show_overdue_reason_without_due_date(self):
        move = self._new_move()

        self.assertFalse(move.show_overdue_reason)

    def test_do_not_show_overdue_reason_on_non_customer_invoice(self):
        due_date = self.today - timedelta(days=1)
        move_types = ("out_refund", "in_invoice", "in_refund", "entry")

        for move_type in move_types:
            with self.subTest(move_type=move_type):
                move = self._new_move(
                    move_type=move_type,
                    invoice_date_due=due_date,
                )

                self.assertFalse(move.show_overdue_reason)
