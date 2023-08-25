# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id', 'quantity', 'uom_id')
    def _onchange_product_id_account_invoice_pricelist(self):

        pricelist = self.invoice_id.pricelist_id

        if not pricelist or not self.invoice_id.partner_id:
            return

        product = self.product_id.with_context(
            lang=self.invoice_id.partner_id.lang,
            partner=self.invoice_id.partner_id.id,
            quantity=self.quantity,
            date_order=self.invoice_id.date_invoice,
            pricelist=pricelist.id,
            uom=self.uom_id.id,
            fiscal_position=(
                self.invoice_id.partner_id.property_account_position_id.id)
        )

        if pricelist.discount_policy == 'without_discount' and product.list_price != 0:
            new_list_price = product.list_price
            if pricelist.currency_id.id != product.currency_id.id:
                product_context = dict(
                    self.env.context,
                    lang=self.invoice_id.partner_id.lang,
                    partner_id=self.invoice_id.partner_id.id,
                    date=self.invoice_id.date_invoice,
                    uom=self.uom_id.id
                )
                new_list_price = self.env['res.currency'].browse(
                    product.currency_id.id).with_context(
                    product_context).compute(
                    new_list_price, pricelist.currency_id
                    )

            discount = (new_list_price - product.price) / new_list_price * 100
            if discount != 0:
                self.discount = discount
        else:
            super(
                AccountInvoiceLine,
                self
                )._onchange_product_id_account_invoice_pricelist()
