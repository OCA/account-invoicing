# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_invoicing_grouping_criteria_id = fields.Many2one(
        string="Purchases Invoicing Grouping Criteria",
        comodel_name="purchase.invoicing.grouping.criteria",
        help="If empty, company default (if any) or default will be applied.",
    )

    @api.model
    def _commercial_fields(self):
        """Add this field to commercial fields, as it should be propagated
        to children.
        """
        return super()._commercial_fields() + [
            "purchase_invoicing_grouping_criteria_id"
        ]
