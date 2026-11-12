# Copyright 2026 Swanand Beedkar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_recipient_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="res_partner_invoice_recipient_rel",
        column1="partner_id",
        column2="recipient_partner_id",
        string="Invoice Recipients",
        domain=[
            ("email", "!=", False),
            "|",
            ("company_id", "=", False),
            ("company_id", "parent_of", "company_id"),
        ],
        help="Additional recipients to receive customer invoices by email.",
    )
