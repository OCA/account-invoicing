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

from openerp.osv import fields, orm


class invoice_force_currency_rate(orm.TransientModel):
    _name = "invoice.force.currency.rate"
    _description = "Force currency rate"

    _columns = {
        'currency_rate': fields.float(
            'Forced currency rate',
            help="You can force the currency rate on the invoice with this "
                 "field.")
        }

    def _get_currency_rate(self, cr, uid, context=None):
        if context is None:
            context = {}
        rate = 1
        if context.get('active_id'):
            invoice = self.pool['account.invoice'].browse(
                cr, uid, context['active_id'], context=context)
            rate = invoice.currency_id.rate
        return rate

    _defaults = {
        'currency_rate': _get_currency_rate,
        }

    def force_currency_rate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('active_id'):
            wizard = self.browse(cr, uid, ids[0], context=context)
            self.pool['account.invoice'].write(
                cr, uid, context['active_id'],
                {'currency_rate': wizard.currency_rate},
                context=context)
        return {'type': 'ir.actions.act_window_close'}
