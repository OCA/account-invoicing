# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
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

from openerp.osv import orm


class account_invoice_refund(orm.TransientModel):

    _inherit = 'account.invoice.refund'

    def invoice_refund(self, cr, uid, ids, context=None):
        context = context or {}

        res = super(account_invoice_refund, self).invoice_refund(
            cr, uid, ids, context=context)

        if 'active_id' in context and 'active_model' in context and \
           context['active_model'] == 'account.invoice':
            account_invoice_pool = self.pool.get(context['active_model'])

            inv = account_invoice_pool.browse(
                cr, uid, context['active_id'], context=context)

            new_id = [d[2][0] for d in res['domain'] if d[0] == 'id']

            data = {'origin': inv.number}
            account_invoice_pool.write(
                cr, uid, new_id, data, context=context)

        return res
