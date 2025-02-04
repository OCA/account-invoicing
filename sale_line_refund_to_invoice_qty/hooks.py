# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    """
    Initialize 'sale_qty_to_reinvoice' field with sql default value
    for performances reasons as Odoo does it with an update instead.
    """
    if openupgrade.column_exists(cr, "account_move_line", "sale_qty_to_reinvoice"):
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
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
