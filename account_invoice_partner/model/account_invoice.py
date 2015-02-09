# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def onchange_partner_id(
            self, invoice_type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        """
        Replace the selected partner with the preferred invoice contact
        """
        partner_invoice_id = partner_id
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            addr_ids = partner.address_get(adr_pref=['invoice'])
            partner_invoice_id = addr_ids['invoice']
        result = super(AccountInvoice, self).onchange_partner_id(
            invoice_type, partner_invoice_id,
            date_invoice=date_invoice, payment_term=payment_term,
            partner_bank_id=partner_bank_id, company_id=company_id)
        if partner_invoice_id != partner_id:
            result['value']['partner_id'] = partner_invoice_id
        return result
