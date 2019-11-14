# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "res.company"

    sale_invoicing_grouping_field_ids = fields.Many2many(
        string="Sale Invoicing Grouping Fields",
        comodel_name='ir.model.fields',
        domain="[('model', '=', 'sale.order')]",
    )
