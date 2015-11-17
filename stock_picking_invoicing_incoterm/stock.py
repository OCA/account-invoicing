# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl
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

from openerp.osv import fields, orm


class StockPicking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'incoterm': fields.many2one(
            'stock.incoterms',
            'Incoterm',
            help="International Commercial Terms are a series of predefined "
            "commercial terms used in international transactions."
        ),
    }

    def _get_invoice_vals(
            self, cr, uid, key,
            inv_type, journal_id, move, context=None):
        invoice_vals = super(StockPicking, self)._get_invoice_vals(
            cr, uid, key, inv_type, journal_id, move, context=context)
        if move.picking_id.incoterm:
            invoice_vals['incoterm'] = move.picking_id.incoterm.id
        return invoice_vals
