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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _prepare_invoice(self, cr, uid, picking,
    	partner, inv_type, journal_id, context=None):
    	invoice_vals = super(stock_picking, self)._prepare_invoice(
    		cr, uid, picking, partner, inv_type, journal_id, context=context)
    	if picking and picking.partner_id:
        	invoice_vals['address_shipping_id'] = picking.partner.id
    	return invoice_vals
