# Copyright (C) 2020-TODAY KMEE
# @author Gabriel Cardoso de Faria <gabriel.cardoso@kmee.com.br>
# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit_invoice(self, inv_type, partner, qty=1):
        result = super()._get_price_unit_invoice(inv_type, partner, qty)
        move = fields.first(self)
        if move.sale_line_id:
            if move._is_kit_component():
                result = move._get_kit_component_price_unit()
            elif move.sale_line_id.price_unit != result:
                result = move.sale_line_id.price_unit

        return result

    # Kit components
    #
    # A phantom kit explodes its sale line into one move per component, all
    # linked to the sale line of the kit. The price belongs to the kit, so each
    # component takes a share of it. The methods below are small on purpose:
    # another module can change the weight (e.g. the BoM line cost_share) or
    # reuse the split for another amount of the sale line (discount, freight).

    def _is_kit_component(self):
        """The move delivers a component of the product sold on its line."""
        self.ensure_one()
        return (
            bool(self.sale_line_id) and self.product_id != self.sale_line_id.product_id
        )

    def _get_kit_component_moves(self):
        """Delivered component moves of the kit line of this move."""
        self.ensure_one()
        return self.sale_line_id._get_kit_component_moves()

    def _get_kit_component_quantity(self):
        self.ensure_one()
        return self.product_uom_qty or self.quantity or 1.0

    def _get_kit_component_weight(self):
        """Weight of the move in the split: its standalone sale value."""
        self.ensure_one()
        return self.product_id.lst_price * self._get_kit_component_quantity()

    def _get_kit_amount(self):
        """Amount of the kit line to split over its components."""
        self.ensure_one()
        line = self.sale_line_id
        return line.price_unit * line.product_uom_qty

    def _get_kit_component_shares(self, amount):
        """Split ``amount`` over the delivered component moves of the kit.

        Proportional to :meth:`_get_kit_component_weight`, or to the quantities
        when no component has a weight. Each share is rounded to the currency
        and the rounding remainder goes to the last move, the one with the
        smallest quantity, so the shares always add up to ``amount``.

        :return: {move: share}
        """
        self.ensure_one()
        moves = self._get_kit_component_moves().sorted(
            lambda m: (-m._get_kit_component_quantity(), m.id)
        )
        if not moves:
            return {}
        currency = self.sale_line_id.currency_id or self.company_id.currency_id
        weights = {move: move._get_kit_component_weight() for move in moves}
        if not any(weights.values()):
            weights = {move: move._get_kit_component_quantity() for move in moves}
        total_weight = sum(weights.values())
        shares = {}
        remainder = amount
        for move in moves[:-1]:
            shares[move] = currency.round(amount * weights[move] / total_weight)
            remainder -= shares[move]
        shares[moves[-1]] = currency.round(remainder)
        return shares

    def _get_kit_component_price_unit(self):
        """Unit price of this component move: its share of the kit price.

        A return move takes the price of the move it returns, so the refund of a
        returned component matches what was invoiced for it.
        """
        self.ensure_one()
        delivered = self
        while delivered.origin_returned_move_id:
            delivered = delivered.origin_returned_move_id
        shares = delivered._get_kit_component_shares(delivered._get_kit_amount())
        if delivered not in shares:
            return self.sale_line_id.price_unit
        price_unit = shares[delivered] / delivered._get_kit_component_quantity()
        return float_round(
            price_unit,
            precision_digits=self.env["decimal.precision"].precision_get(
                "Product Price"
            ),
        )

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        move = fields.first(self)
        if move.sale_line_id:
            company = move.sale_line_id.order_id.company_id
            if company.sale_invoicing_policy in ("stock_picking", "both"):
                values["invoice_state"] = "2binvoiced"

        return values
