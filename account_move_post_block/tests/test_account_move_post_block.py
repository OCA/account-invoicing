# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestAccountMovePostBlock(TransactionCase):
    def setUp(self):
        super(TestAccountMovePostBlock, self).setUp()
        self.users_obj = self.env["res.users"]
        self.am_obj = self.env["account.move"].with_context(check_move_validity=False)
        self.am_block_obj = self.env["account.post.block.reason"]
        # company
        self.company1 = self.env.ref("base.main_company")
        # groups
        self.group_account_user = self.env.ref("account.group_account_invoice")
        self.group_account_manager = self.env.ref("account.group_account_manager")
        # Partner
        self.partner1 = self.env.ref("base.res_partner_1")
        # Products
        self.product1 = self.env.ref("product.product_product_7")
        self.product2 = self.env.ref("product.product_product_9")
        self.product3 = self.env.ref("product.product_product_11")
        # Accounts
        self.account_receivable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        # Create users
        self.user1_id = self._create_user(
            "user_1", [self.group_account_user], self.company1
        )
        self.user2_id = self._create_user(
            "user_2", [self.group_account_manager], self.company1
        )
        # Create a AM Block Reason
        self._create_block_reason()

    def _create_block_reason(self):
        self.am_post_block_reason = self.am_block_obj.create(
            {"name": "Needs Permission", "description": "Permission to validate"}
        )

    def _create_user(self, login, groups, company):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user = self.users_obj.with_context(no_reset_password=True).create(
            {
                "name": "Account User",
                "login": login,
                "password": "test",
                "email": "test@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user.id

    def _create_account_move(self, line_products):
        """Create a account move.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                "name": product.name,
                "product_id": product.id,
                "quantity": qty,
                "price_unit": 100,
                "account_id": self.account_receivable.id,
            }
            lines.append((0, 0, line_values))
        account_move = self.am_obj.create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner1.id,
                "line_ids": lines,
                "company_id": self.company1.id,
            }
        )
        return account_move
