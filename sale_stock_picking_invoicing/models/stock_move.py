# Copyright (C) 2020-TODAY KMEE
# @author Gabriel Cardoso de Faria <gabriel.cardoso@kmee.com.br>
# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit_invoice(self, inv_type, partner, qty=1):
        result = super()._get_price_unit_invoice(inv_type, partner, qty)
        move = fields.first(self)
        if move.sale_line_id:
            if move.product_id != move.sale_line_id.product_id:
                # A phantom kit explodes the sale line into component moves:
                # each component delivers a product that is not the one sold.
                # The price belongs to the kit, so the component takes its
                # share of it instead of the full kit price.
                result = move._get_kit_component_price_unit()
            elif move.sale_line_id.price_unit != result:
                result = move.sale_line_id.price_unit

        return result

    def _get_kit_component_price_unit(self):
        """Share of the sold price of a kit falling on this component move.

        The sold amount of the sale line is distributed over its component
        moves in proportion to the standalone sale prices of the components,
        which is how the fiscal documents expect the kit to be broken down:
        the invoice then totals exactly the price the kit was sold for.
        """
        self.ensure_one()
        line = self.sale_line_id
        components = line.move_ids.filtered(
            lambda m: m.state != "cancel" and m.product_id != line.product_id
        )

        def quantity(component):
            return component.product_uom_qty or component.quantity or 1.0

        amount = line.price_unit * line.product_uom_qty
        weights = {
            component: component.product_id.list_price * quantity(component)
            for component in components
        }
        total_weight = sum(weights.values())
        if not total_weight:
            # components without a sale price: split the amount evenly
            total_quantity = sum(quantity(c) for c in components) or 1.0
            return amount / total_quantity
        return amount * weights[self] / total_weight / quantity(self)

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        move = fields.first(self)
        if move.sale_line_id:
            company = move.sale_line_id.order_id.company_id
            if company.sale_invoicing_policy in ("stock_picking", "both"):
                values["invoice_state"] = "2binvoiced"

        return values
