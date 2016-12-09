# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id_account_invoice_pricelist(self):
        if not self.invoice_id.pricelist_id or not self.invoice_id.partner_id:
            return
        product = self.product_id.with_context(
            lang=self.invoice_id.partner_id.lang,
            partner=self.invoice_id.partner_id.id,
            quantity=self.quantity,
            date_order=self.invoice_id.date_invoice,
            pricelist=self.invoice_id.pricelist_id.id,
            uom=self.uom_id.id,
            fiscal_position=(
                self.invoice_id.partner_id.property_account_position_id.id)
        )
        self.price_unit = self.env['account.tax']._fix_tax_included_price(
            product.price, product.taxes_id, self.invoice_line_tax_ids)
