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
        " for reporting.")

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
           
    
#    , type, partner_id, date_invoice=False, payment_term=False,
#            partner_bank_id=False, company_id=False):
                
#        partner_obj = self.env['res.partner']
        res = super(AccountInvoice, self)._onchange_partner_id()
#            type, partner_id, date_invoice=date_invoice,
#            payment_term=payment_term, partner_bank_id=partner_bank_id,
#            company_id=company_id)
        pricelist_id = False

        if self.partner_id:
#            partner = partner_obj.browse(partner_id)
            if self.type in ('out_invoice', 'out_refund'):
                # Customer Invoices
                pricelist_id = self.partner_id.property_product_pricelist
            elif self.type in ('in_invoice', 'in_refund'):
                # Supplier Invoices
                if self.partner_id._model._columns.get(
                        'property_product_pricelist_purchase', False):
                    pricelist_id =\
                        self.partner_id.property_product_pricelist_purchase
            self.pricelist_id = pricelist_id
#        res['value']['pricelist_id'] = pricelist_id
        return res
    
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        
        if self.invoice_id.pricelist_id:
            pricelist_id=self.invoice_id.pricelist_id
            product = self.product_id.with_context(
                                         partner=self.partner_id.id,
                                         quantity=self.quantity,
                                         date=self.invoice_id.date_invoice,
                                         pricelist= pricelist_id.id,
                                         uom=self.uom_id.id
                                        )
            print("price unit %s" % product.price)
            print("self.partner_id.id %s" % self.partner_id.id)
            print ("self.quantity, %s" % self.quantity)
            print ("self.invoice_id.date, %s" % self.invoice_id.date)
            print("pricelist= pricelist_id, %s" % pricelist_id)
            print("self.uom_id %s" % self.uom_id)
            self.price_unit = product.price 
        return res