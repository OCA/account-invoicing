# -*- coding: utf-8 -*-
##############################################################################

#     This file is part of account_invoice_line_sort, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_line_sort is free software: you can redistribute it
#     and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     account_invoice_line_sort is distributed in the hope that it will
#     be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with account_invoice_line_sort.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from operator import attrgetter 

AVAILABLE_SORT_OPTIONS = [
    ('sequence', 'Sequence'),
    ('name', 'Description'),
    ('price_unit', 'Unit Price'),
    ('price_subtotal', 'Amount'),
]
AVAILABLE_ORDER_OPTIONS = [
    ('asc', 'Ascending'),
    ('desc', 'Descending')
]


class account_invoice(models.Model):
    _inherit = "account.invoice"
    _sort_trigger_fields = ('line_order',
                            'line_order_direction')

    line_order = fields.Selection(AVAILABLE_SORT_OPTIONS,
                                  "Sort Lines By",
                                  default='sequence')
    line_order_direction = fields.Selection(AVAILABLE_ORDER_OPTIONS,
                                            "Sort Direction",
                                            default='asc')

    @api.model
    def get_partner_sort_options(self, partner_id):
        res = {}
        if partner_id:
            p = self.env['res.partner'].browse(partner_id)
            res['line_order'] = p.line_order
            res['line_order_direction'] = p.line_order_direction
        return res

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        res = super(account_invoice,
                    self).onchange_partner_id(type,
                                              partner_id,
                                              date_invoice=date_invoice,
                                              payment_term=payment_term,
                                              partner_bank_id=partner_bank_id,
                                              company_id=company_id)
        if partner_id:
            res['value'].update(self.get_partner_sort_options(partner_id))
        return res

    @api.one
    def _sort_account_invoice_line(self):
        if self.invoice_line:
            sequence = 0
            key = attrgetter(self.line_order)
            reverse = self.line_order_direction == 'desc'
            for line in self.invoice_line.sorted(key=key, reverse=reverse):
                sequence += 10
                line.sequence = sequence

    @api.multi
    def write(self, vals):
        sort = False
        fields = [key for key in vals if key in self._sort_trigger_fields]
        if fields:
            if [key for key in fields if vals[key] != self[key]]:
                sort = True
        res = super(account_invoice, self).write(vals)
        if sort or 'invoice_line' in vals:
            self._sort_account_invoice_line()
        return res

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if not [key for key in vals if key in self._sort_trigger_fields]:
            partner_id = vals.get('partner_id', False)
            vals.update(self.get_partner_sort_options(partner_id))
        invoice = super(account_invoice, self).create(vals)
        invoice._sort_account_invoice_line()
        return invoice


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    _sort_trigger_fields = ('name', 'quantity', 'price_unit', 'discount')

    @api.multi
    def write(self, vals):
        sort = False
        fields = [key for key in vals if key in self._sort_trigger_fields]
        if fields:
            if [key for key in fields if vals[key] != self[key]]:
                sort = True
        res = super(account_invoice_line, self).write(vals)
        if sort:
            self.invoice_id._sort_account_invoice_line()
        return res

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        line = super(account_invoice_line, self).create(vals)
        self.invoice_id._sort_account_invoice_line()
        return line
