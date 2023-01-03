# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestAccountInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create an invoice with its payment unblocked
        cls.account_move = cls.env["account.move"].create({"payment_blocked": False})

    def test_payment_blocked(self):
        # Blocked boolean set to true rises a ValidationError
        self.assertFalse(self.account_move.payment_blocked)
        self.account_move.payment_blocked = True
        with self.assertRaises(UserError):
            self.account_move.action_register_payment()
        self.account_move.payment_blocked = False
        self.account_move.action_register_payment()
