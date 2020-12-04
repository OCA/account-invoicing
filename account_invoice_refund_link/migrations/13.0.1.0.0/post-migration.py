# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET origin_line_id = aml2.id
        FROM account_invoice_line_refunds_rel rel,
            account_move_line aml2
        WHERE rel.refund_line_id = aml.old_invoice_line_id
            AND rel.original_line_id = aml2.old_invoice_line_id""",
    )
