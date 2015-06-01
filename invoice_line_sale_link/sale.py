# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Chafique Delli
#    Copyright 2014 Akretion SA
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


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def _prepare_order_line_invoice_line(self, cr, uid,
                                         line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=False, context=context)
        res['sale_line_id'] = line.id
        return res
