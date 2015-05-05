# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl (<http://www.agilebg.com>)
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


class AccountInvoiceLine(orm.Model):

    def _get_uom_data(self, cr, uid, ids, field_name, arg, context):
        res = {}
        sale_line_obj = self.pool['sale.order.line']
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'uom_id': False,
                'uom_qty': False,
            }
            if line.move_line_ids and len(line.move_line_ids) == 1:
                res[line.id]['uom_id'] = (
                    line.move_line_ids[0].product_uom.id
                    if line.move_line_ids[0].product_uom else False
                )
                res[line.id]['uom_qty'] = line.move_line_ids[0].product_qty
            else:
                so_line_ids = sale_line_obj.search(
                    cr, uid, [('invoice_lines', 'in', [line.id])],
                    context=context
                )
                if len(so_line_ids) == 1:
                    so_line = sale_line_obj.browse(
                        cr, uid, so_line_ids[0], context=context)
                    res[line.id]['uom_id'] = (
                        so_line.product_uom.id
                        if so_line.product_uom else False
                    )
                    res[line.id]['uom_qty'] = so_line.product_uom_qty
        return res

    _inherit = "account.invoice.line"
    _columns = {
        'uom_id': fields.function(
            _get_uom_data, string="Internal UoM", type="many2one",
            relation='product.uom', multi="uom"),
        'uom_qty': fields.function(
            _get_uom_data, string="Internal quantity", type="float",
            digits_compute=dp.get_precision('Product UoS'), multi="uom")
    }
