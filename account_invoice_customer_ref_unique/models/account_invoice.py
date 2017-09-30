# -*- coding: utf-8 -*-
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
from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    customer_ref_strip = fields.Char(
        compute='_compute_customer_ref_strip', store=True)

    @api.multi
    @api.depends('name')
    def _compute_customer_ref_strip(self):
        for invoice in self:
            invoice_type = invoice.type
            if invoice_type not in ['out_invoice', 'out_refund']:
                return True
            if invoice.name:
                invoice.customer_ref_strip = invoice.name.lower()
    _sql_constraints = [
        ('unique_customer_ref_strip', 'UNIQUE('
         'customer_ref_strip, company_id, commercial_partner_id)',
         _('The customer reference must be unique for '
           'each customer !'))]
