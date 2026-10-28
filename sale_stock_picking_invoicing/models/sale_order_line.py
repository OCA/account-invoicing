# Copyright (C) 2013-Today - Akretion (<http://www.akretion.com>).
# @author Renato Lima <renato.lima@akretion.com.br>
# @author Raphael Valyi <raphael.valyi@akretion.com>
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        if self.order_id.company_id.sale_invoicing_policy in (
            "stock_picking",
            "both",
        ):
            values["invoice_state"] = "2binvoiced"

        return values

    def _get_kit_component_moves(self):
        """Delivered moves of the components a phantom kit line exploded into.

        Return moves keep the sale line, so they are left out: the split of the
        kit price and the quantities of a kit are based on what was delivered.
        """
        self.ensure_one()
        return self.move_ids.filtered(
            lambda m: m.state != "cancel"
            and m.product_id != self.product_id
            and m.location_dest_id.usage == "customer"
            and not m.origin_returned_move_id
        )
