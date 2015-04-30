# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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

from openerp.osv import orm


class StockMove(orm.Model):
    _inherit = "stock.move"

    def _get_invoice_line_vals(
            self, cr, uid, move, partner, inv_type, context=None):
        res = super(StockMove, self)._get_invoice_line_vals(
            cr, uid, move, partner, inv_type, context=context)
        if move:
            user = self.pool['res.users'].browse(
                cr, uid, uid, context=context)
            user_groups = [g.id for g in user.groups_id]
            ref = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'account_invoice_line_no_picking_name',
                'group_not_use_picking_name_per_invoice_line'
            )
            if ref and len(ref) > 1 and ref[1]:
                group_id = ref[1]
                if group_id in user_groups:
                    res['name'] = move.name
        return res
