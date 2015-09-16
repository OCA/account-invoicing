# -*- coding: utf-8 -*-
##############################################################################
#
#    account_group_invoice_lines module for Odoo
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author: Sébastien LANGE <sebastien.lange@syleam.fr>
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

    def inv_line_characteristic_hashcode(self, invoice_line):
        '''When grouping per account, we remove the product_id from
        the hashcode.
        WARNING: I suppose that the other methods that inherit this
        method add data on the end of the hashcode, not at the beginning.
        This is the case of github/OCA/account-closing/
        account_cutoff_prepaid/account.py'''
        res = super(AccountInvoice, self).inv_line_characteristic_hashcode(
            invoice_line)
        if self.journal_id.group_method == 'account':
            hash_list = res.split('-')
            # remove product_id from hashcode
            hash_list.pop(2)
            res = '-'.join(hash_list)
        return res

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        if (
                self.journal_id.group_invoice_lines and
                self.journal_id.group_method == 'account'):
            res['name'] = '/'
            res['product_id'] = False
        return res


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    group_method = fields.Selection([
        ('product', 'By Product'),
        ('account', 'By Account')
        ], string='Group by', default='account',
        help="If you select 'By Product', the account move lines generated "
        "when you validate an invoice will be "
        "grouped by product, account, analytic account and tax code. "
        "If you select 'By Account', they will be grouped by account, "
        "analytic account and tax code, without taking into account "
        "the product.")
