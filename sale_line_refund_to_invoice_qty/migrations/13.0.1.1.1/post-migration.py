# Copyright 2021 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def sale_qty_to_reinvoice_swapping(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move_line aml
            SET sale_qty_to_reinvoice = true
            WHERE aml.{} = false
        """.format(
            openupgrade.get_legacy_name("sale_qty_not_to_reinvoice")
        ),
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move_line aml
            SET sale_qty_to_reinvoice = false
            WHERE aml.{} = true
        """.format(
            openupgrade.get_legacy_name("sale_qty_not_to_reinvoice")
        ),
    )


@openupgrade.migrate()
def migrate(env, version):
    sale_qty_to_reinvoice_swapping(env)
