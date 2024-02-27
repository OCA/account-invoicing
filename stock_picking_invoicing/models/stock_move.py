# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.float_utils import float_round


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

        if inv_type in ("in_invoice", "in_refund"):
            price_unit = min(self.mapped("price_unit"))
        else:
            price_unit = max(self.mapped("price_unit"))

        if price_unit > 0.0:
            # Value informed by user should has preferency
            return price_unit

        product = self.mapped("product_id")
        product.ensure_one()
        sum(self.mapped("product_uom_qty"))
        product_uom = self.mapped("product_uom")
        company = fields.first(self).picking_id.company_id
        # Only in the cases the stock.move has linked to Sale or
        # Purchase Order it's possible use different Currencys
        # TODO: Should this module make possible by include field
        #  currency_id in Stock.picking?
        currency = company.currency_id
        pickings = self.mapped("picking_id")
        date_done = min(pickings.mapped("date_done"))

        if inv_type in ("in_invoice", "in_refund"):

            seller = product._select_seller(
                partner_id=partner, quantity=qty, date=date_done
            )
            if not seller:
                po_line_uom = self.mapped("product_uom") or product.uom_po_id
                price_unit = self.env["account.tax"]._fix_tax_included_price_company(
                    product.uom_id._compute_price(product.standard_price, po_line_uom),
                    product.supplier_taxes_id,
                    # TODO: Should inform taxes_ids in stock.move?
                    product.supplier_taxes_id,
                    fields.first(self).company_id,
                )
                price_unit = product.currency_id._convert(
                    price_unit, currency, company, date_done, False
                )
                result = float_round(
                    price_unit,
                    precision_digits=max(
                        currency.decimal_places,
                        self.env["decimal.precision"].precision_get("Product Price"),
                    ),
                )
            else:
                price_unit = self.env["account.tax"]._fix_tax_included_price_company(
                    seller.price,
                    product.supplier_taxes_id,
                    # TODO: Should inform taxes_ids in stock.move?
                    product.supplier_taxes_id,
                    fields.first(self).company_id,
                )
                price_unit = seller.currency_id._convert(
                    price_unit, currency, company, date_done, False
                )
                price_unit = float_round(
                    price_unit,
                    precision_digits=max(
                        currency.decimal_places,
                        self.env["decimal.precision"].precision_get("Product Price"),
                    ),
                )
                result = seller.product_uom._compute_price(price_unit, product_uom)

        else:
            # If partner given, search price in its sale pricelist
            fiscal_position = (
                self.env["account.fiscal.position"]
                .with_company(company)
                ._get_fiscal_position(partner)
            )

            if partner and partner.property_product_pricelist:
                price_unit = None
                pricelist_rule_id = (
                    partner.property_product_pricelist._get_product_rule(
                        product,
                        qty or 1.0,
                        uom=product_uom,
                        date=date_done,
                    )
                )
                pricelist_rule = self.env["product.pricelist.item"].browse(
                    pricelist_rule_id
                )
                price_unit = pricelist_rule._compute_price(
                    product,
                    qty,
                    product_uom,
                    date_done,
                    currency=currency,
                )

            else:
                price_unit = product.lst_price

            result = product._get_tax_included_unit_price(
                company,
                currency,
                date_done,
                "sale",
                fiscal_position=fiscal_position,
                product_price_unit=price_unit,
                product_currency=currency,
            )

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
