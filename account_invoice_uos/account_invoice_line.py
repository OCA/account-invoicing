# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#    Author: Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class account_invoice_line(orm.Model):

    def _get_uos_data(self, cr, uid, ids, field_name, arg, context):
        res = {}
        sale_line_obj = self.pool['sale.order.line']
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'sale_uos_id': False,
                'sale_uos_qty': False,
                }
            so_line_ids = sale_line_obj.search(cr, uid, [
                ('invoice_lines', 'in', [line.id]),
                ], context=context)
            if len(so_line_ids) == 1:
                so_line = sale_line_obj.browse(
                    cr, uid, so_line_ids[0], context=context)
                res[line.id]['sale_uos_id'] = (
                    so_line.product_uos.id if so_line.product_uos else False)
                res[line.id]['sale_uos_qty'] = so_line.product_uos_qty
        return res

    _inherit = "account.invoice.line"
    _columns = {
        'sale_uos_id': fields.function(
            _get_uos_data, string="UoS", type="many2one",
            relation='product.uom', multi="uos"),
        'sale_uos_qty': fields.function(
            _get_uos_data, string="Quantity (UoS)", type="float",
            digits_compute=dp.get_precision('Product UoS'), multi="uos")
        }
