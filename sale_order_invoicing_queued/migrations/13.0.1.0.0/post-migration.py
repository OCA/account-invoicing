# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Change queue_job stored values referenced to account.invoice model
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE queue_job
        SET model_name='account.move',
            records = replace(records, 'account.invoice', 'account.move')
        WHERE name='sale.order.create_invoices_job' AND model_name='account.invoice';
    """,
    )
