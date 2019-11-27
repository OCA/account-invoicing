# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_invoicing_grouping_criteria_id = fields.Many2one(
        string="Sales Invoicing Grouping Criteria",
        comodel_name="sale.invoicing.grouping.criteria",
        help="If empty, company default (if any) or default will be applied.",
    )

    @api.model
    def _commercial_fields(self):
        """Add this field to commercial fields, as it should be propagated
        to children.
        """
        return super()._commercial_fields() + ["sale_invoicing_grouping_criteria_id"]
