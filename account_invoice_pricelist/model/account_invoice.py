# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist', string='Pricelist',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_account_invoice_pricelist(self):
        if self.type not in ('out_invoice', 'out_refund'):
            return
        if self.partner_id.property_product_pricelist:
            self.pricelist_id = \
                self.partner_id.property_product_pricelist.id

    @api.multi
    def button_update_prices_from_pricelist(self):
        for invoice in self:
            invoice.invoice_line_ids.filtered(
                'product_id')._onchange_product_id_account_invoice_pricelist()
