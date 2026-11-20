# Copyright (C) 2019-Today: Odoo Community Association
# @ 2019-Today: Akretion - www.akretion.com.br -
#   Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.fields import Domain


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    count_picking_2binvoiced = fields.Integer(compute="_compute_picking_2binvoiced")

    def _compute_picking_2binvoiced(self):
        domain = [
            ("picking_type_id", "in", self.ids),
            ("invoice_state", "=", "2binvoiced"),
            ("state", "!=", "cancel"),
        ]
        grouped_data = self.env["stock.picking"]._read_group(
            domain=Domain(domain),
            groupby=["picking_type_id"],
            aggregates=["id:count"],
        )
        count_map = {res[0][0]: res[1] for res in grouped_data}
        for record in self:
            record.count_picking_2binvoiced = count_map.get(record, 0)
