# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMoveRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_purchase_user = cls.env.ref("purchase.group_purchase_user")
        cls.group_account_readonly = cls.env.ref("account.group_account_readonly")

        cls.restricted_user = cls.env["res.users"].create(
            {
                "name": "Test Purchase & Readonly User",
                "login": "test_restricted_user",
                "email": "test@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.group_purchase_user.id,
                            cls.group_account_readonly.id,
                            cls.env.ref("base.group_user").id,
                        ],
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.move = cls.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": cls.partner.id,
                "invoice_date": "2026-01-01",
            }
        )
        cls.move_restricted = cls.move.with_user(cls.restricted_user)

    def test_restricted_user_cannot_create_move(self):
        """User cannot create account.move"""

        move_model_restricted = self.env["account.move"].with_user(self.restricted_user)

        with self.assertRaises(AccessError):
            move_model_restricted.create(
                {
                    "move_type": "in_invoice",
                    "partner_id": self.partner.id,
                }
            )

    def test_restricted_user_cannot_write_move(self):
        """User cannot modify an existing account.move"""

        with self.assertRaises(AccessError):
            self.move_restricted.write({"ref": "Modified by restricted user"})

    def test_restricted_user_cannot_unlink_move(self):
        """User cannot delete an existing account.move"""

        with self.assertRaises(AccessError):
            self.move_restricted.unlink()

    def test_restricted_user_can_read_move(self):
        """User can read an existing account.move"""
        _ = self.move_restricted.read(["name", "state"])
