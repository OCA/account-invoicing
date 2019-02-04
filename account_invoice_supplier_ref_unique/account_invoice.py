# coding: utf-8
###############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    supplier_invoice_number = fields.Char(copy=False)

    @api.constrains('supplier_invoice_number', 'date_invoice')
    def _check_unique_supplier_invoice_number_insensitive(self):
        if (self.supplier_invoice_number and
                self.date_invoice and self.type in
                ('in_invoice', 'in_refund')):
            same_supplier_inv_num = self.search([
                ('commercial_partner_id', '=', self.commercial_partner_id.id),
                ('type', 'in', ('in_invoice', 'in_refund')),
                ('supplier_invoice_number',
                 '=ilike',
                 self.supplier_invoice_number),
                ('id', '!=', self.id),
            ])
            if same_supplier_inv_num:
                for inv in same_supplier_inv_num:
                    year_inv_date = datetime.strptime(inv.date_invoice,
                                                      '%Y-%m-%d').year
                    self_year_inv_date = datetime.strptime(self.date_invoice,
                                                           '%Y-%m-%d').year
                    if year_inv_date == self_year_inv_date:
                        suppl_year_inv_date = datetime.strptime(
                            same_supplier_inv_num[0].date_invoice,
                            '%Y-%m-%d').year
                        raise ValidationError(
                            _(
                                "The invoice/refund with supplier "
                                "invoice number '%s' "
                                "of year '%s' "
                                "already exists in Odoo under the number '%s' "
                                "for supplier '%s'.") % (
                                same_supplier_inv_num[
                                    0].supplier_invoice_number,
                                suppl_year_inv_date,
                                same_supplier_inv_num[0].number or '-',
                                same_supplier_inv_num[
                                    0].partner_id.display_name))
