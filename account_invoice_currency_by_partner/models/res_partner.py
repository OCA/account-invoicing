# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    vendor_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Vendor Currency",
        help="If field, this value set currency in vendor bills for this partner",
        company_dependent=True,
    )
    customer_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Customer Currency",
        help="If field, this value set currency in customer bills for this partner",
        company_dependent=True,
    )
