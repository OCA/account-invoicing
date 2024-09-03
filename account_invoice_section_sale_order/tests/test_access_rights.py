# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import tagged

from .common import Common


@tagged("-at_install", "post_install")
class TestAccessRights(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassUser()

    @classmethod
    def setUpClassUser(cls):
        cls.create_only_group = cls.env["res.groups"].create(
            {"name": "Create Only Group"}
        )
        cls.sale_manager_group = cls.env.ref("sales_team.group_sale_manager")
        cls.env["ir.model.access"].create(
            [
                {
                    "name": "invoice_create_only",
                    "model_id": cls.env.ref("account.model_account_move").id,
                    "group_id": cls.create_only_group.id,
                    "perm_read": 0,
                    "perm_write": 0,
                    "perm_create": 1,
                    "perm_unlink": 0,
                },
                {
                    "name": "invoice_line_create_only",
                    "model_id": cls.env.ref("account.model_account_move_line").id,
                    "group_id": cls.create_only_group.id,
                    "perm_read": 0,
                    "perm_write": 0,
                    "perm_create": 1,
                    "perm_unlink": 0,
                },
            ]
        )
        cls.create_only_user = cls.env["res.users"].create(
            {
                "name": "Create Only User",
                "login": "createonlyuser@example.com",
                "groups_id": [
                    (6, 0, (cls.create_only_group | cls.sale_manager_group).ids),
                ],
            }
        )

    def test_access_rights(self):
        orders = self.order1_p1 + self.order2_p1
        # We're testing that no exception is raised while creating invoices
        # with a user having only create access on the invoices models
        invoice_ids = orders.with_user(self.create_only_user)._create_invoices()
        self.assertTrue(bool(invoice_ids))
