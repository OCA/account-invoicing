# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    to_be_sent_with_account_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice that should send this attachment",
    )
