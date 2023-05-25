# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = [
        _name,
        "stock.invoice.state.mixin",
    ]

    def _get_price_unit_invoice(self, inv_type, partner, qty=1):
        """
        Gets price unit for invoice
        :param inv_type: str
        :param partner: res.partner
        :param qty: float
        :return: float
        """
        product = self.mapped("product_id")
        product.ensure_one()
        if inv_type in ("in_invoice", "in_refund"):
            result = product.price
        else:
            # If partner given, search price in its sale pricelist
            if partner and partner.property_product_pricelist:
                product = product.with_context(
                    partner=partner.id,
                    quantity=qty,
                    pricelist=partner.property_product_pricelist.id,
                    uom=fields.first(self).product_uom.id,
                )
                result = product.price
            else:
                result = product.lst_price
        return result

    def _prepare_extra_move_vals(self, qty):
        """Copy invoice state for a new extra stock move"""
        values = super()._prepare_extra_move_vals(qty)
        values["invoice_state"] = self.invoice_state
        return values

    def _prepare_move_split_vals(self, uom_qty):
        """Copy invoice state for a new splitted stock move"""
        values = super()._prepare_move_split_vals(uom_qty)
        values["invoice_state"] = self.invoice_state
        return values
