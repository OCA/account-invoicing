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


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'currency_rate': fields.float(
            'Forced currency rate',
            help="You can force the currency rate on the invoice with this "
                 "field.")
        }

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
