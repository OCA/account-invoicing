# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company
        SET invoice_line_sequence_recompute = true;
        """,
    )
