# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account - Pricelist on Invoices for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Column Section
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist', string='Pricelist',
        help="The pricelist of the partner, when the invoice is created"
        " or the partner has changed. This is a technical field used"
        " for reporting.",
        readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False, payment_term=False,
            partner_bank_id=False, company_id=False):
        partner_obj = self.env['res.partner']
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        pricelist_id = False
        if partner_id:
            partner = partner_obj.browse(partner_id)
            if type in ('out_invoice', 'out_refund'):
                # Customer Invoices
                pricelist_id = partner.property_product_pricelist.id
            elif type in ('in_invoice', 'in_refund'):
                # Supplier Invoices
                if partner._model._columns.get(
                        'property_product_pricelist_purchase', False):
                    pricelist_id =\
                        partner.property_product_pricelist_purchase.id
        res['value']['pricelist_id'] = pricelist_id
        return res

    @api.multi
    def button_update_prices_from_pricelist(self):
        for this in self:
            this.invoice_line.filtered('product_id').update_from_pricelist()
            this.button_reset_taxes()
