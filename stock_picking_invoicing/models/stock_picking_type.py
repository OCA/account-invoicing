# Copyright (C) 2019-Today: Odoo Community Association
# @ 2019-Today: Akretion - www.akretion.com.br -
#   Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    count_picking_2binvoiced = fields.Integer(compute="_compute_picking_2binvoiced")

    def _compute_picking_2binvoiced(self):
        domain = [
            ("state", "!=", "cancel"),
            ("invoice_state", "=", "2binvoiced"),
            ("picking_type_id", "in", self.ids),
        ]
        # Single grouped query for the whole recordset; the count is looked up
        # by picking type.
        counts = {
            picking_type.id: count
            for picking_type, count in self.env["stock.picking"]._read_group(
                domain, ["picking_type_id"], ["__count"]
            )
        }
        for record in self:
            record.count_picking_2binvoiced = counts.get(record.id, 0)
