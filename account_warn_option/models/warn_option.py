# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class WarnOption(models.Model):
    _inherit = "warn.option"

    allowed_warning_usage = fields.Selection(
        selection_add=[
            ("partner_invoice_warn", "(Partner) Warning on the Invoice"),
        ],
        ondelete={
            "partner_invoice_warn": "set default",
        },
    )
