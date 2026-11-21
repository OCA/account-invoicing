# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import Command
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestAccountInvoice(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "customer_rank": 1,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "list_price": 100.0,
            }
        )
        # create an invoice with its payment unblocked
        cls.account_move = cls.env["account.move"].create(
            {
                "payment_blocked": False,
                "partner_id": cls.customer.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def test_payment_blocked(self):
        # Blocked boolean set to true rises a ValidationError
        self.assertFalse(self.account_move.payment_blocked)
        self.account_move.action_post()
        self.account_move.payment_blocked = True
        with self.assertRaises(UserError):
            self.account_move.action_register_payment()
        self.account_move.payment_blocked = False
        self.account_move.action_register_payment()
