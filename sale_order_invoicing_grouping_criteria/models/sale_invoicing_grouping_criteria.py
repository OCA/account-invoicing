# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleInvoicingGroupingCriteria(models.Model):
    _name = "sale.invoicing.grouping.criteria"
    _description = "Sales Invoicing Grouping Criteria"

    name = fields.Char()
    field_ids = fields.Many2many(
        string="Grouping Fields",
        comodel_name="ir.model.fields",
        domain="[('model', '=', 'sale.order')]",
        help="Fields used for grouping sales orders when invoicing. "
        "Invoicing address and currency will always be applied.",
    )
