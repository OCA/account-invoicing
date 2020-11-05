# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(
        env.cr,
        {
            "account_invoice_global_discount": [("invoice_id", None)],
            "account_invoice_global_discount_rel": [("invoice_id", None)],
        },
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_invoice_global_discount ADD invoice_id INT4"
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_invoice_global_discount_rel ADD invoice_id INT4"
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """UPDATE account_invoice_global_discount aigd
            SET invoice_id = ai.move_id
            FROM account_invoice ai
            WHERE ai.id = aigd.{}"""
        ).format(sql.Identifier(openupgrade.get_legacy_name("invoice_id"))),
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """UPDATE account_invoice_global_discount_rel aigdr
            SET invoice_id = ai.move_id
            FROM account_invoice ai
            WHERE ai.id = aigdr.{}"""
        ).format(sql.Identifier(openupgrade.get_legacy_name("invoice_id"))),
    )
