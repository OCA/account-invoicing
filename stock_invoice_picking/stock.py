# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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
from openerp.tools.translate import _


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _get_partner_to_invoice(self, cr, uid, picking, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = super(stock_picking, self)._get_partner_to_invoice(
            cr, uid, picking, context=context)
        if isinstance(partner, int):
            partner = partner_obj.browse(cr, uid, partner, context=context)
        if picking.partner_id.id != partner.id:
            # if someone else modified invoice partner, I use it
            return partner.id
        return partner_obj.address_get(
            cr, uid, [partner.id], ['invoice'], context=context
        )['invoice']

    def set_to_be_invoiced(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids, context):
            if picking.invoice_state == '2binvoiced':
                raise orm.except_orm(
                    _('Error'),
                    _(
                        "Can't update invoice control for picking %s: "
                        "It's 'to be invoiced' yet"
                    ) % picking.name
                )
            if picking.invoice_state in ('none', 'invoiced'):
                if picking.invoice_id:
                    raise orm.except_orm(_('Error'), _(
                        'Picking %s has linked invoice %s'
                    ) % (picking.name, picking.invoice_id.number))
                picking.write({'invoice_state': '2binvoiced'})
        return True


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    def set_to_be_invoiced(self, cr, uid, ids, context=None):
        # override in order to redirect to stock.picking object
        return self.pool.get('stock.picking').set_to_be_invoiced(
            cr, uid, ids, context=context)


class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'

    def set_to_be_invoiced(self, cr, uid, ids, context=None):
        # override in order to redirect to stock.picking object
        return self.pool.get('stock.picking').set_to_be_invoiced(
            cr, uid, ids, context=context)
