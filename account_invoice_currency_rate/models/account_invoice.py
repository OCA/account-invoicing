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
from openerp.tools.translate import _


class account_invoice(models.Model):
    _inherit = "account.invoice"


    currency_rate = fields.Float(
        'Forced currency rate',
        help="You can force the currency rate on the invoice with this field.",
        copy=False,
    )
    label_rate = fields.Char(copy=False)
    show_force_currency = fields.Boolean(default=False, copy=False,
        compute='_show_force_currency', store=True,
    )
    
    def _show_force_currency(self):
        currency_company = self.company_id.currency_id
        return currency_company.id.id != self.currency_id.id
    
    @api.model
    def _get_currency_rate(self, currency_id=None):
        rate = 1
        currency_company = self.company_id.currency_id

        if not currency_id:
            currency_id = currency_company

        rate = self.pool.get('res.currency').compute(
            self._cr, self._uid, currency_id.id, currency_company.id, 1,
        )
        return rate
    
    _defaults = {
        'currency_rate': 1,
    }
    
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.currency_rate = self._get_currency_rate(self.currency_id)
        self.label_rate = ' '.join([
            _('Currency rate:'), self.currency_id.name, '1.00 =',
            self.company_id.currency_id.name,
        ])

    def action_move_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            if invoice.currency_rate:
                ctx['force_currency_rate'] = invoice.currency_rate
            super(account_invoice, self).action_move_create(
                cr, uid, [invoice.id], context=ctx)
        return True
