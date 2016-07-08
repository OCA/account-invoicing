# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api


class account_invoice(models.Model):
    _inherit = "account.invoice"

    currency_rate = fields.Float(
        'Forced currency rate', compute='_get_currency_rate', store=True,
        help="You can force the currency rate on the invoice with this field.",
        copy=False,
    )

    label_rate = fields.Char(compute='_get_currency_rate_label')

    is_multi_currency = fields.Boolean(
        string = 'Multi Currency Invoice',
        compute = '_get_currency_rate',
        store = True,
        help='Fields with internal purpose only that depicts if the '
        'invoice is a multi currency one or not'
    )

    _defaults = {
        'is_multi_currency': False,
    }

    @api.depends('currency_id', 'date_invoice')
    @api.onchange('date_invoice')
    def _get_currency_rate(self):
        user = self.env.user
        company_id = self.env.context.get('company_id', user.company_id.id)
        company = self.env['res.company'].browse(company_id)

        rate = self.currency_id.with_context(
            date= self.date_invoice
        ).compute(1, company.currency_id)

        self.is_multi_currency = self.currency_id != company.currency_id
        self.currency_rate = rate

    @api.one
    @api.depends('currency_rate')
    @api.onchange('currency_rate')
    def _get_currency_rate_label(self):
        label_rate = ' '.join([
            '1.00', self.currency_id.name, '=', str(self.currency_rate),
            self.company_id.currency_id.name,
        ])
        self.label_rate = label_rate

    def action_move_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            if invoice.currency_rate != 1.00:
                ctx['force_currency_rate'] = invoice.currency_rate
            super(account_invoice, self).action_move_create(
                cr, uid, [invoice.id], context=ctx)
        return True
