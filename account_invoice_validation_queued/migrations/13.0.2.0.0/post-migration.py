# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.table_exists(env.cr, "account_move_queue_job_rel"):
        return
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_move_validation_job_rel
        (invoice_id, job_id)
        SELECT rel.invoice_id, rel.job_id
        FROM account_move_queue_job_rel rel
        JOIN queue_job qj ON qj.id = rel.job_id
        WHERE qj.method_name = 'action_invoice_open_job'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_move_queue_job_rel
        WHERE job_id IN (
            SELECT rel.job_id
            FROM account_move_queue_job_rel rel
            JOIN queue_job qj ON qj.id = rel.job_id
            WHERE qj.method_name = 'action_invoice_open_job'
        )
        """,
    )
