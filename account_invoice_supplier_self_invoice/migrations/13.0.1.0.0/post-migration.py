# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET self_invoice_number = ai.self_invoice_number,
            set_self_invoice = ai.set_self_invoice
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id and ai.self_invoice_number is not null""",
    )
