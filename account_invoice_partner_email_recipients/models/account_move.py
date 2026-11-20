# Copyright 2026 Swanand Beedkar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_recipient_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="account_move_invoice_recipient_rel",
        column1="move_id",
        column2="recipient_partner_id",
        string="Invoice Recipients",
        compute="_compute_invoice_recipient_ids",
        store=True,
        readonly=False,
        domain=[
            ("email", "!=", False),
            "|",
            ("company_id", "=", False),
            ("company_id", "parent_of", "company_id"),
        ],
        help="Additional recipients who will receive this invoice by email.",
    )

    @api.depends("partner_id", "commercial_partner_id", "company_id")
    def _compute_invoice_recipient_ids(self):
        for move in self:
            if move.is_sale_document(include_receipts=True):
                partner = move.partner_id
                recipients = partner.invoice_recipient_ids
                if not recipients and move.commercial_partner_id:
                    recipients = move.commercial_partner_id.invoice_recipient_ids
                move.invoice_recipient_ids = recipients
            else:
                move.invoice_recipient_ids = self.env["res.partner"]
