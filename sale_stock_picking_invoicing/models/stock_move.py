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
        if move.sale_line_id and move.sale_line_id.price_unit != result:
            result = move.sale_line_id.price_unit

        return result

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        move = fields.first(self)
        if move.sale_line_id:
            company = move.sale_line_id.order_id.company_id
            if company.sale_invoicing_policy == "stock_picking":
                values["invoice_state"] = "2binvoiced"

        return values
