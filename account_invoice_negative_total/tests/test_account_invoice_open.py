# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestInvoiceNegativeAmount(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test"})
        self.account_type = self.env["account.account.type"].create(
            {"name": "Test Regular", "type": "other"}
        )
        self.account = self.env["account.account"].create(
            {
                "name": "Test",
                "code": "TEST",
                "user_type_id": self.account_type.id,
                "reconcile": False,
            }
        )
        self.journal = self.env["account.journal"].search(
            [("type", "=", "sale")])[0]

        self.invoice_line = self.env["account.invoice.line"].create(
            {
                "name": "Line",
                "price_unit": 1000.0,
                "account_id": self.account.id,
                "quantity": -1,
            }
        )

        self.invoice = self.env["account.invoice"].create(
            {
                "name": "Test Customer Invoice",
                "journal_id": self.journal.id,
                "partner_id": self.partner.id,
                "account_id": self.account.id,
                "invoice_line_ids": [(4, self.invoice_line.id)],
            }
        )

    def test_invoice_has_negative_amount(self):
        self.assertEqual(
            float_compare(
                self.invoice.amount_total,
                0.0,
                precision_rounding=self.invoice.currency_id.rounding,
            ),
            -1,
        )

    def test_action_invoice_open_without_permission(self):
        with self.assertRaises(UserError):
            self.invoice.action_invoice_open()

    def test_action_invoice_open_with_permissions(self):
        # create a user with the right permission group
        self.user_with_permission = self.env["res.users"].create(
            {
                "name": "test",
                "login": "test",
                "email": "test",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref(
                                "account.group_account_manager"
                                ).id,
                            self.env.ref(
                                "account_invoice_negative_total.group_validate_invoice_negative_total_amount" # noqa
                            ).id,
                        ],
                    )
                ],
            }
        )
        self.permission_env = self.env["account.invoice"].sudo(
            self.user_with_permission
        )
        # check that the user can open the invoice with a negative amount
        self.assertTrue(
            self.permission_env.browse(self.invoice.id).action_invoice_open()
        )
        # reset the state of the invoice for further tests
        self.permission_env.browse(self.invoice.id).state = "draft"
