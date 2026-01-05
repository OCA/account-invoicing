# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    receipt_status = fields.Selection(
        related="purchase_line_id.line_receipt_status",
        string="Receipt Status",
        readonly=True,
        store=True,
        related_sudo=True,
    )
