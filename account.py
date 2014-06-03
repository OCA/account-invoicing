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

from datetime import datetime
from openerp import Model, api, fields


class account_invoice(Model):
    _inherit = 'account.invoice'

    @api.multi
    def inv_line_characteristic_hashcode(self, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        if self.journal_id.group_method == 'product':
            return super(account_invoice, self).inv_line_characteristic_hashcode(invoice_line)
        return "%s-%s-%s-%s" % (
            invoice_line['account_id'],
            invoice_line.get('tax_code_id', "False"),
            invoice_line.get('analytic_account_id', "False"),
            invoice_line.get('date_maturity', "False"))


class account_move(Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        """
        Change name of account move line if we group invoice line
        """
        super(account_move, self).post()
        invoice = self.env.context['invoice']
        if invoice.journal_id.group_invoice_lines and invoice.journal_id.group_method == 'account':
            lang = self.env['res.users'].context_get()['lang']
            res_lang_ids = self.env['res.lang'].search([('code', '=', lang)], limit=1)
            format_date = res_lang_ids.date_format
            for move in self:
                if move.name != '/':
                    date_due = invoice.date_due and datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime(format_date) or ''
                    move.line_id.write({'name': move.name.ljust(20) + date_due})
        return True


class account_journal(Model):
    _inherit = 'account.journal'

    group_method = fields.Selection([
        ('product', 'By Product'),
        ('account', 'By Account Accountant')
    ], string='Group by', default='product', help='By default, OpenERP group by product but if choice by account accountant, the name of account move line will be invoice number with maturity date')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
