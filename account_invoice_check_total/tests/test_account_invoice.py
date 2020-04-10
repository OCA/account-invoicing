# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..models.account_invoice import GROUP_AICT


class TestAccountInvoice(TransactionCase):
    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        # ENVIRONEMENTS

        self.account_move = self.env["account.move"]
        self.account_model = self.env["account.account"]
        self.account_move_line = self.env["account.move.line"]
        self.current_user = self.env.user
        # Add current user to group: group_supplier_inv_check_total
        self.env.ref(GROUP_AICT).write({"users": [(4, self.current_user.id)]})

        # INSTANCES

        # Instance: Account
        self.invoice_account = self.account_model.search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        # Instance: Invoice Line
        self.move_line = self.account_move_line.new(
            {
                "name": "Test invoice line",
                "account_id": self.invoice_account.id,
                "quantity": 1.000,
                "price_unit": 2.99,
            }
        )

    def test_action_move_create(self):
        # Creation of an invoice instance, wrong check_total
        # Result: UserError
        invoice = self.account_move.create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                # 'account_id': self.invoice_account.id,
                "type": "in_invoice",
                "check_total": 1.19,
                "invoice_line_ids": [(6, 0, [self.move_line.id])],
            }
        )

        invoice.line_ids._onchange_price_subtotal()
        self.assertEqual(invoice.check_total, 1.19)
        self.assertEqual(invoice.check_total_display_difference, -1.80)
        with self.assertRaises(ValidationError):
            invoice.action_move_create()

    def test_onchange_check_total(self):
        invoice = self.account_move.create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "account_id": self.invoice_account.id,
                "type": "in_invoice",
                "check_total": 1.19,
                "invoice_line_ids": [(6, 0, [self.move_line.id])],
            }
        )

        invoice.invoice_line_ids.ensure_one()
        invoice.invoice_line_ids.price_unit = 5.99
        invoice.line_ids._onchange_price_subtotal()
        invoice.onchange_check_total()
        self.assertEqual(invoice.check_total, 1.19)
        self.assertEqual(invoice.check_total_display_difference, -4.80)
