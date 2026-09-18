# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_purchase_invoicing_grouping_criteria_id = fields.Many2one(
        string="Default Purchases Invoicing Grouping Criteria",
        comodel_name="purchase.invoicing.grouping.criteria",
    )
