# -*- coding: utf-8 -*-
# © 2015-2016 GRAP <http://www.grap.coop>.
# © 2017 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later <http://www.gnu.org/licenses/agpl.html>.
from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if not self.product_id or not self.invoice_id.pricelist_id:
            return res
        partner = self.invoice_id.partner_id
        pricelist = self.invoice_id.pricelist_id
        if self.uom_id != self.product_id.uom_id.id:
            pricedict = pricelist.with_context(
                uom=self.uom_id.id
            ).price_get(self.product_id.id, self.quantity, partner.id)
        else:
            pricedict = pricelist.price_get(self.product_id, self.quantity,
                                            partner.id)
        self.price_unit = pricedict[pricelist.id]
        currency = self.invoice_id.currency_id
        if currency:
            company = self.invoice_id.company_id
            if company.currency_id != currency:
                self.price_unit = pricelist.currency_id.compute(
                    self.price_unit, currency, round=True
                )
        return res

    @api.multi
    def update_from_pricelist(self):
        """overwrite current prices from pricelist"""
        for line in self.filtered(lambda r: r.invoice_id.state == 'draft'):
            line._onchange_product_id()
