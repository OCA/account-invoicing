# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    whole_delivered_invoiceability = fields.Boolean(
        help="Prevent invoicing until everything has been delivered."
    )

    @api.model
    def _commercial_fields(self):
        """Add this field to commercial fields, as it should be propagated
        to children.
        """
        return super()._commercial_fields() + ["whole_delivered_invoiceability"]
