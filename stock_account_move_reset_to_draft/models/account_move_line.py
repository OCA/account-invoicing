# Copyright 2024 Tecnativa - Víctor Martínez
# Copyright 2026 ACSONE SA/NV (https://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero

from odoo.addons.account.models.account_move_line import AccountMoveLine as MoveLine


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_intertwined_valuation_at_draft(self, soft=False) -> MoveLine:
        """
        This will check if stock valuations are not intertwined.

        Raise an error if the user has no rights to force the reset to draft,
        else, returns the concerned line.
        """
        intertwined_lines = self.browse()
        for line in self:
            origin_svls = line.stock_valuation_layer_ids.stock_valuation_layer_id
            if (
                len(
                    origin_svls.stock_valuation_layer_ids.account_move_line_id.filtered(
                        lambda x: x.parent_state == "posted"
                    )
                )
                > 1
            ):
                if soft:
                    intertwined_lines |= line
                else:
                    raise UserError(
                        _(
                            "Inventory valuation records are intertwined for %(line_name)s.",
                            line_name=self.display_name,
                        )
                    )
        return intertwined_lines

    def _check_consumed_valuation_at_draft(self, soft=False) -> MoveLine:
        """
        Check if the incoming valuations haven't been consumed already.

        If the user has no rights to force the reset to draft, raises an error,
        else, return the concerned lines.
        """
        lines_with_consumed_values = self.browse()
        for line in self:
            origin_svls = line.stock_valuation_layer_ids.stock_valuation_layer_id
            for origin_svl in origin_svls:
                if origin_svl.quantity != origin_svl.remaining_qty:
                    if soft:
                        lines_with_consumed_values |= line
                        continue
                    raise UserError(
                        _(
                            "The inventory has already been (partially) consumed "
                            "for %(line_name)s.",
                            line_name=line.display_name,
                        )
                    )
        return lines_with_consumed_values

    def _revert_stock_valuation_at_draft(self):
        """
        If products having valuation layers linked to this account move line
        haven't been consumed, revert them
        in order to be regenerated at account move post.
        """
        for line in self:
            origin_svls = line.stock_valuation_layer_ids.stock_valuation_layer_id
            revert_stock_valuation_layers = self.env["stock.valuation.layer"].browse()
            for origin_svl in origin_svls:
                svls = origin_svl.stock_valuation_layer_ids.filtered(
                    "account_move_line_id"
                )
                value = sum(svls.mapped("value"))
                if not float_is_zero(
                    value, precision_rounding=line.currency_id.rounding
                ):
                    origin_svl.remaining_value -= value
                    revert_stock_valuation_layers |= svls[0].copy({"value": -value})
            if revert_stock_valuation_layers:
                revert_stock_valuation_layers._validate_accounting_entries()
            product = line.product_id.with_company(line.move_id.company_id.id)
            if product.cost_method == "average":
                product.sudo().with_context(disable_auto_svl=True).write(
                    {"standard_price": product.value_svl / product.quantity_svl}
                )
