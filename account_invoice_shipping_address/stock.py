# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#    Author: Nicola Malcontenti <nicola.malcontenti@agilebg.com>
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

from openerp import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_invoice_vals(self, cr, uid, key, inv_type,
                          journal_id, move, context=None):
        invoice_vals = super(StockPicking, self)._get_invoice_vals(
            cr, uid, key, inv_type, journal_id, move, context=context)
        if move and move.partner_id:
            if 'delivery_address_id' in self.env['stock.picking']._fields:
                invoice_vals['address_shipping_id'] = (
                    move.picking_id.delivery_address_id and
                    move.picking_id.delivery_address_id.id or
                    move.picking_id.partner_id.id)
            else:
                invoice_vals[
                    'address_shipping_id'] = move.picking_id.partner_id.id
        return invoice_vals
