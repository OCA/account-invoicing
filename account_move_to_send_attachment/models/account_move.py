# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.api import NewId


class AccountMove(models.Model):
    _inherit = "account.move"

    to_be_sent_attachment_ids_domain = fields.Binary(
        compute="_compute_to_be_sent_attachment_ids_domain",
    )

    to_be_sent_attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        string="Extra Attachments (To be Sent)",
        inverse_name="to_be_sent_with_account_move_id",
        inverse="_inverse_to_be_sent_attachment_ids",
    )

    @api.depends("attachment_ids")
    def _compute_to_be_sent_attachment_ids_domain(self):
        for move in self:
            move_origin = move
            if isinstance(move.id, NewId):
                move_origin = move._origin
            move.to_be_sent_attachment_ids_domain = [
                ("res_id", "=", move_origin.id),
                ("res_model", "=", move_origin._name),
            ]

    def _inverse_to_be_sent_attachment_ids(self):
        """
        Ensure attachments are linked to record
        """
        for move in self:
            to_add_attachments = move.to_be_sent_attachment_ids - move.attachment_ids
            move.attachment_ids |= to_add_attachments
