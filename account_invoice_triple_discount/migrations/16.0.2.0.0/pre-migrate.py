# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


def migrate_discount_to_discount1(env):
    openupgrade.add_fields(
        env,
        [
            (
                "discount1",
                "account.move.line",
                "account_move_line",
                "float",
                "numeric",
                "account_invoice_triple_discount",
                0.0,
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET discount1 = discount;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    migrate_discount_to_discount1(env)
