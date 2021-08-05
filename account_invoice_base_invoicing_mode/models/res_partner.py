# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoicing_mode = fields.Selection([("standard", "Standard")], default="standard")
    one_invoice_per_order = fields.Boolean(
        "One invoice per order",
        default=False,
        help="Do not group sale order into one invoice.",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + [
            "invoicing_mode",
            "one_invoice_per_order",
        ]
