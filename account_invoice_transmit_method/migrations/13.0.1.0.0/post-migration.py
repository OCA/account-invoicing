# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET transmit_method_id = ai.transmit_method_id,
            transmit_method_code = ai.transmit_method_code
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id""",
    )
