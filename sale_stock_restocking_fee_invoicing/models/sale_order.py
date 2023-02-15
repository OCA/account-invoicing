# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.fields import Command


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_restocking_fee_line_name(self, stock_move):
        """Return the de name for the so line. This method should be called
        with the customer lang into the context to get the description into
        the right language
        """
        lang = self.partner_id.lang
        return _(
            f"Restocking fee for {stock_move.product_uom_qty} "
            f"{stock_move.product_uom.with_context(lang=lang).name} "
            f"{stock_move.sale_line_id.name}"
        )

    def _get_restocking_fee_line_value(self, stock_move):
        self.ensure_one()
        product_id = self.company_id.restocking_fee_product_id
        if not product_id:
            raise UserError(
                _(
                    "No product configured for restocking fee. "
                    "Please fix the configuration into stock settings or "
                    "contact you administrator."
                )
            )
        name = self.with_context(
            lang=self.partner_id.lang
        )._get_restocking_fee_line_name(stock_move=stock_move)

        values = {
            "order_id": self.id,
            "name": name,
            "product_uom_qty": 1,
            "product_uom": product_id.uom_id.id,
            "product_id": product_id.id,
            "is_restocking_fee": True,
        }
        if self.order_line:
            values["sequence"] = self.order_line[-1].sequence + 1
        return values

    def _get_restocking_fee_lines_values(self, stock_moves):
        self.ensure_one()
        vals = []
        sequence = self.order_line[-1].sequence if self.order_line else 1
        for move in stock_moves:
            sequence += 1
            values = self._get_restocking_fee_line_value(move)
            values["sequence"] = sequence
            vals.append(values)
        return vals

    def _charge_restocking_fee(self, stock_moves):
        lines = self._get_restocking_fee_lines_values(stock_moves)
        values = [Command.create(line) for line in lines]
        self.sudo().write({"order_line": values})
