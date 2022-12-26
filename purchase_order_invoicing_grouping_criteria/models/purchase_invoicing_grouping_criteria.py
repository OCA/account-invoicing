# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseInvoicingGroupingCriteria(models.Model):
    _name = "purchase.invoicing.grouping.criteria"
    _description = "Purchases Invoicing Grouping Criteria"

    name = fields.Char()
    field_ids = fields.Many2many(
        string="Grouping Fields",
        comodel_name="ir.model.fields",
        domain="[('model', '=', 'purchase.order')]",
        help="Fields used for grouping purchases orders when invoicing. "
        "Partner, company and currency will always be applied.",
    )
