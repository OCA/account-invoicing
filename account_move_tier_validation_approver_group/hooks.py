from odoo.tools import sql


def pre_init_hook(env):
    """Prepare new account.move.approver_group_id computed field.

    Add column to avoid MemoryError on an existing Odoo instance
    with lots of data.
    """
    if not sql.column_exists(env.cr, "account_move", "approver_group_id"):
        sql.create_column(env.cr, "account_move", "approver_group_id", "int4")
