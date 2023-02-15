# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_customer_return = fields.Boolean(compute="_compute_is_customer_return")

    is_customer_out = fields.Boolean(compute="_compute_is_customer_out")

    @api.depends("location_id")
    def _compute_is_customer_return(self):
        for rec in self:
            rec.is_customer_return = rec.location_id.usage == "customer"

    @api.depends("location_dest_id")
    def _compute_is_customer_out(self):
        for rec in self:
            rec.is_customer_out = rec.location_dest_id.usage == "customer"
