# -*- encoding: utf-8 -*-
# #############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
###############################################################################






from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
   

    @api.multi
    @api.constrains('name')
    def _check_unique_name_insensitive(self):
        for invoice in self:            
            invoice_type = invoice.type
            invoice_partner = invoice.partner_id

            if invoice_type not in ['out_invoice', 'out_refund']:
                return True

            invoice_obj=self.env['account.invoice'].search([("type", "=", invoice_type),
                                  ("partner_id", "=", invoice_partner.id)])          


            lst = [
                x.name.lower() for x in invoice_obj
                if x.name and x.id != invoice.id
            ]
            if invoice.name and invoice.name.lower()  in lst:
                raise ValidationError(_('The customer reference must be unique for each customer !'))
            

    
