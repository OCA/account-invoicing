# -*- coding: utf-8 -*-
##############################################################################
#
#    account_group_invoice_lines module for OpenERP, Change method to group invoice lines in account
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of account_group_invoice_lines
#
#    account_group_invoice_lines is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    account_group_invoice_lines is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
from datetime import datetime


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def inv_line_characteristic_hashcode(self, invoice, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        if invoice.journal_id.group_method == 'product':
            return super(account_invoice, self).inv_line_characteristic_hashcode(invoice, invoice_line)
        return "%s-%s-%s-%s" % (
            invoice_line['account_id'],
            invoice_line.get('tax_code_id', "False"),
            invoice_line.get('analytic_account_id', "False"),
            invoice_line.get('date_maturity', "False"))

account_invoice()


class account_move(osv.osv):
    _inherit = 'account.move'

    def post(self, cr, uid, ids, context=None):
        """
        Change name of account move line if we group invoice line
        """
        super(account_move, self).post(cr, uid, ids, context=context)
        invoice = context.get('invoice', False)
        if invoice and invoice.journal_id.group_invoice_lines and invoice.journal_id.group_method == 'account':
            lang = self.pool.get('res.users').context_get(cr, uid)['lang']
            res_lang_obj = self.pool.get('res.lang')
            res_lang_ids = res_lang_obj.search(cr, uid, [('code', '=', lang)], limit=1, context=context)
            format_date = res_lang_obj.browse(cr, uid, res_lang_ids[0], context=context).date_format
            move_line_obj = self.pool.get('account.move.line')
            for move in self.browse(cr, uid, ids, context=context):
                if move.name != '/':
                    date_due = invoice.date_due and datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime(format_date) or ''
                    move_line_obj.write(cr, uid, [line.id for line in move.line_id], {
                        'name': move.name.ljust(20) + date_due
                    }, context=context)
        return True

account_move()


class account_journal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'group_method': fields.selection([('product', 'By Product'), ('account', 'By Account Accountant')], 'Group by', help='By default, OpenERP group by product but if choice by account accountant, the name of account move line will be invoice number with maturity date'),
    }

    _defaults = {
        'group_method': 'product',
    }

account_journal()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
