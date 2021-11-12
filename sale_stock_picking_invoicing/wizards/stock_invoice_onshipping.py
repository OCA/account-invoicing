# Copyright (C) 2020-TODAY KMEE
# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInvoiceOnshipping(models.TransientModel):

    _inherit = "stock.invoice.onshipping"

    def _build_invoice_values_from_pickings(self, pickings):
        invoice, values = super()._build_invoice_values_from_pickings(pickings)
        pick = fields.first(pickings)
        if pick.sale_id:
            values.update(
                {
                    "partner_id": pick.sale_id.partner_invoice_id.id,
                }
            )
            if (
                pick.sale_id.partner_invoice_id.id
                != pick.sale_id.partner_shipping_id.id
            ):
                values.update(
                    {
                        "partner_shipping_id": pick.sale_id.partner_shipping_id.id,
                    }
                )
            if pick.sale_id.payment_term_id.id != values["invoice_payment_term_id"]:
                values.update(
                    {"invoice_payment_term_id": pick.sale_id.payment_term_id.id}
                )
            # TODO: Should we implement payment_mode_id as did in Brazilian
            #  Localization?
            # The field payment_mode_id are implement by
            # https://github.com/OCA/bank-payment/tree/14.0/account_payment_mode
            # To avoid the necessity of a 'GLUE' module we just check
            # if the fiel exist.
            # if hasattr(pick.sale_id, "payment_mode_id"):
            #    if pick.sale_id.payment_mode_id.id != values.get("payment_mode_id"):
            #        values.update({"payment_mode_id": pick.sale_id.payment_mode_id.id})
            if pick.sale_id.note:
                values.update({"narration": pick.sale_id.note})

        return invoice, values

    # Check the comment below
    # def _get_picking_key(self, picking):
    #    key = super()._get_picking_key(picking)
    #    if picking.sale_id:
    #        key = key + (
    #            picking.sale_id.payment_term_id,
    #            picking.sale_id.fiscal_position_id,
    #            picking.sale_id.commitment_date,
    #            picking.sale_id.analytic_account_id,
    #            picking.sale_id.pricelist_id,
    #            picking.sale_id.company_id,
    #        )
    #    return key

    def _get_move_key(self, move):
        key = super()._get_move_key(move)
        if move.sale_line_id:
            # TODO: Analise if Sale Lines should be grouped.
            #  For now remains a problem https://github.com/odoo/odoo/pull/77195
            #  with field qty_invoiced at sale.order.line, when a invoice line
            #  has more than one sale line related the field show the total QTY
            #  of those lines, e.g:
            #  product_uom_qty | qty_invoiced
            #       2.0        |  4.0
            # key = key + (
            #    move.sale_line_id.price_unit,
            #    move.sale_line_id.customer_lead,
            #    move.sale_line_id.currency_id,
            #    move.sale_line_id.tax_id,
            #    move.sale_line_id.analytic_tag_ids,
            # )
            key = key + (move.sale_line_id,)

        return key

    def _get_invoice_line_values(self, moves, invoice_values, invoice):
        values = super()._get_invoice_line_values(moves, invoice_values, invoice)
        move = fields.first(moves)
        if move.sale_line_id:
            values["sale_line_ids"] = [(6, 0, moves.sale_line_id.ids)]
            values[
                "analytic_account_id"
            ] = moves.sale_line_id.order_id.analytic_account_id.id
            values["analytic_tag_ids"] = [
                (6, 0, moves.sale_line_id.analytic_tag_ids.ids)
            ]

        return values
