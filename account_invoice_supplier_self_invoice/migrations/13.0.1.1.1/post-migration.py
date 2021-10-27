# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET ref = self_invoice_number
        WHERE ref IS NULL AND self_invoice_number IS NOT NULL""",
    )
