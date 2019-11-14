# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_sale_invoicing_grouping_criteria_id = fields.Many2one(
        string="Default Sales Invoicing Grouping Criteria",
        comodel_name='sale.invoicing.grouping.criteria',
    )
