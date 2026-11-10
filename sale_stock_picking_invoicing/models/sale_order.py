# Copyright (C) 2020-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        lines = super()._get_invoiceable_lines(final)
        model = self.env.context.get("active_model")
        if (
            self.company_id.sale_invoicing_policy == "stock_picking"
            and model != "stock.picking"
        ):
            new_lines = lines.filtered(
                lambda ln: ln.product_id.type != "product" and not ln.is_downpayment
            )
            if new_lines:
                # Case lines with Product Type 'service'
                lines = new_lines
            else:
                # Case only Products Type 'product'
                raise UserError(
                    _(
                        "When 'Sale Invoicing Policy' is defined as"
                        "'Stock Picking' the Invoice can only be created"
                        " from the Stock Picking, if necessary you can change"
                        " in the Company or Sale Settings."
                    )
                )

        return lines
