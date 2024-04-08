# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _add_one_invoice_per_shipping(env):
    if not openupgrade.column_exists(env.cr, "sale_order", "one_invoice_per_shipping"):
        field_spec = [
            (
                "one_invoice_per_shipping",
                "sale.order",
                "sale_order",
                "boolean",
                "boolean",
                "partner_invoicing_mode_at_shipping",
                False,
            )
        ]
        openupgrade.add_fields(env, field_spec)


def pre_init_hook(env):
    _add_one_invoice_per_shipping(env)
