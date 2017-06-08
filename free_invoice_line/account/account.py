# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm
import decimal_precision as dp
from tools.translate import _


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    _columns = {
        'free': fields.boolean('For Free'),
    }


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_untaxed_free': 0.0,
                'amount_tax_free': 0.0,
                'amount_total': 0.0
            }
            lines = {}
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
                if line.free:
                    res[invoice.id]['amount_untaxed_free'] += (
                        line.price_subtotal)
                    # costruiamo un dizionario chiave=iva e valore=imponibile
                    for tax in line.invoice_line_tax_id:
                        if tax.amount in lines:
                            lines[tax.amount] += line.price_subtotal
                        else:
                            lines[tax.amount] = line.price_subtotal
            for tl in lines:
                res[invoice.id]['amount_tax_free'] += lines[tl] * (1 + tl)
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = (
                res[invoice.id]['amount_tax'] +
                res[invoice.id]['amount_untaxed'])
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['account.invoice.line'].browse(cr, uid, ids,
                                                             context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool['account.invoice.tax'].browse(cr, uid, ids,
                                                           context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed_free': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='"For Free" Amount',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_tax_free': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='"For Free" Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_untaxed': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id'], 20),
            },
            multi='all'),
    }

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        if invoice_browse.amount_untaxed_free > 0.0:
            precision = self.pool['decimal.precision'].precision_get(cr, 1,
                                                                     'Account')
            precision_diff = round(
                invoice_browse.amount_tax_free -
                invoice_browse.amount_untaxed_free, precision)
            account_id = self.pool['account.invoice.line']._default_account_id(
                cr, uid, {'type': 'out_invoice'})
            if (invoice_browse.amount_untaxed_free ==
                    invoice_browse.amount_untaxed):
                # se imponibile = imponibile omaggio
                move_lines[-1][2]['account_id'] = account_id
                move_lines[-1][2]['date_maturity'] = False
            move_lines[-1][2]['debit'] -= invoice_browse.amount_tax_free

            # riga imponibile omaggio
            new_line = {
                'analytic_account_id': False,
                'tax_code_id': False,
                'analytic_lines': [],
                'tax_amount': False,
                'name': _('"For Free" Amount'),
                'ref': '',
                'analytics_id': False,
                'currency_id': False,
                'debit': invoice_browse.amount_untaxed_free,
                'product_id': False,
                'date_maturity': False,
                'credit': False,
                'date': move_lines[0][2]['date'],
                'amount_currency': 0,
                'product_uom_id': False,
                'quantity': 1,
                'partner_id': move_lines[0][2]['partner_id'],
                'account_id': account_id,
            }
            move_lines += [(0, 0, new_line)]
            # riga iva omaggio
            new_line = {
                'analytic_account_id': False,
                'tax_code_id': False,
                'analytic_lines': [],
                'tax_amount': False,
                'name': _('"For Free" Tax Amount'),
                'ref': '',
                'analytics_id': False,
                'currency_id': False,
                'debit': precision_diff,
                'product_id': False,
                'date_maturity': False,
                'credit': False,
                'date': move_lines[0][2]['date'],
                'amount_currency': 0,
                'product_uom_id': False,
                'quantity': 1,
                'partner_id': move_lines[0][2]['partner_id'],
                'account_id': account_id,
            }
            move_lines += [(0, 0, new_line)]
        return move_lines

account_invoice()
