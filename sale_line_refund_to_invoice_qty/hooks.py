# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(env):
    """
    Initialize 'sale_qty_to_reinvoice' field with sql default value
    for performances reasons as Odoo does it with an update instead.
    """
    if openupgrade.column_exists(env.cr, "account_move_line", "sale_qty_to_reinvoice"):
        return

    field_spec = [
        (
            "sale_qty_to_reinvoice",
            "account.move.line",
            "account_move_line",
            "boolean",
            "boolean",
            "sale_line_refund_to_invoice_qty",
            True,
        )
    ]
    openupgrade.add_fields(env, field_spec=field_spec)
