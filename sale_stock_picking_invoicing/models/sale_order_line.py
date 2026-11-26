# Copyright (C) 2013-Today - Akretion (<http://www.akretion.com>).
# @author Renato Lima <renato.lima@akretion.com.br>
# @author Raphael Valyi <raphael.valyi@akretion.com>
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, models

INVOICE_SIGN = {"out_invoice": 1, "out_refund": -1}


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

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity")
    def _compute_qty_invoiced(self):
        """Count kits, not component units, on a phantom kit line.

        Invoiced from the picking, a kit line is invoiced through one line per
        component, all linked to the kit line. The quantity invoiced is the
        number of kits those lines cover, as mrp does for the delivered
        quantity, instead of the sum of the component quantities.
        """
        res = super()._compute_qty_invoiced()
        for line in self:
            per_kit = line._get_kit_component_quantities()
            if per_kit:
                line.qty_invoiced = line._get_kit_qty_invoiced(per_kit)
        return res

    def _get_kit_component_quantities(self):
        """Quantity of each component in one kit (in the unit of the line).

        :return: {component product: quantity in its UoM}, empty when the line
                 was not exploded into component moves.
        """
        self.ensure_one()
        if not self.product_uom_qty:
            return {}
        quantities = defaultdict(float)
        for move in self._get_kit_component_moves():
            quantities[move.product_id] += move.product_qty
        return {
            product: qty / self.product_uom_qty
            for product, qty in quantities.items()
            if qty
        }

    def _get_kit_qty_invoiced(self, per_kit):
        self.ensure_one()
        kit_qty = 0.0
        components = defaultdict(float)
        for invoice_line in self._get_invoice_lines():
            move = invoice_line.move_id
            sign = INVOICE_SIGN.get(move.move_type)
            if not sign or (
                move.state == "cancel" and move.payment_state != "invoicing_legacy"
            ):
                continue
            product = invoice_line.product_id
            uom = invoice_line.product_uom_id
            if product in per_kit:
                components[product] += sign * uom._compute_quantity(
                    invoice_line.quantity, product.uom_id, round=False
                )
            else:  # the kit itself, e.g. invoiced from the sale order
                kit_qty += sign * uom._compute_quantity(
                    invoice_line.quantity, self.product_uom, round=False
                )
        return kit_qty + min(
            components[product] / qty for product, qty in per_kit.items()
        )
