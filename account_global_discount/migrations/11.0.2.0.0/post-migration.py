# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    # Link the new field that points to the invoice global discount instead
    # of the global discount definition
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
        UPDATE account_move_line aml
        SET invoice_global_discount_id = aigd.id
        FROM account_invoice_global_discount aigd
        WHERE aigd.invoice_id = aml.invoice_id
            AND aigd.global_discount_id = aml.{}
        """
        ).format(sql.Identifier(openupgrade.get_legacy_name("global_discount_id"))),
    )
    # Link to existing global discount records, all the invoice taxes as best
    # effort
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_invoice_global_discount_account_tax_rel
        (account_invoice_global_discount_id, account_tax_id)
        SELECT aigd.id, ailt.tax_id
        FROM account_invoice_global_discount aigd
        JOIN account_invoice_line ail ON aigd.invoice_id = ail.invoice_id
        JOIN account_invoice_line_tax ailt ON ailt.invoice_line_id = ail.id
        GROUP BY aigd.id, ailt.tax_id""",
    )
    # Delete in prevention of manual manipulations existing tax lines linked
    # to global discount journal items
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_move_line_account_tax_rel rel
            USING account_move_line aml
        WHERE rel.account_move_line_id = aml.id
            AND aml.invoice_global_discount_id IS NOT NULL""",
    )
    # Link all invoice taxes in global discount existing journal items as best
    # effort
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_move_line_account_tax_rel
        (account_move_line_id, account_tax_id)
        SELECT aml.id, rel.account_tax_id
        FROM account_move_line aml
        JOIN account_invoice_global_discount_account_tax_rel rel
            ON rel.account_invoice_global_discount_id =
                aml.invoice_global_discount_id""",
    )
