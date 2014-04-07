# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl
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


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'incoterm': fields.many2one(
            'stock.incoterms',
            'Incoterm',
            help="International Commercial Terms are a series of predefined\
            commercial terms used in international transactions."
        ),
    }

    def _prepare_invoice_group(
            self, cr, uid, picking,
            partner, invoice, context=None):
        invoice_vals = super(stock_picking, self)._prepare_invoice_group(
            cr, uid, picking, partner, invoice, context)
        if picking.incoterm:
            invoice_vals['incoterm'] = picking.incoterm.id
        return invoice_vals

    def _prepare_invoice(
            self, cr, uid, picking,
            partner, inv_type, journal_id, context=None):
        invoice_vals = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)
        if picking.incoterm:
            invoice_vals['incoterm'] = picking.incoterm.id
        return invoice_vals


class stock_picking_in(orm.Model):
    _inherit = "stock.picking.in"

    _columns = {
        'incoterm': fields.many2one(
            'stock.incoterms',
            'Incoterm',
            help="International Commercial Terms are a series of predefined\
            commercial terms used in international transactions."
        ),
    }

    def _prepare_invoice_group(
            self, cr, uid, picking,
            partner, invoice, context=None):
        return self.pool.get('stock.picking')._prepare_invoice_group(
            cr, uid, picking, partner, invoice, context=context)

    def _prepare_invoice(
            self, cr, uid, picking,
            partner, inv_type, journal_id, context=None):
        return self.pool.get('stock.picking')._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)


class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"

    _columns = {
        'incoterm': fields.many2one(
            'stock.incoterms',
            'Incoterm',
            help="International Commercial Terms are a series of predefined\
            commercial terms used in international transactions."
        ),
    }

    def _prepare_invoice_group(
            self, cr, uid, picking,
            partner, invoice, context=None):
        return self.pool.get('stock.picking')._prepare_invoice_group(
            cr, uid, picking, partner, invoice, context=context)

    def _prepare_invoice(
            self, cr, uid, picking,
            partner, inv_type, journal_id, context=None):
        return self.pool.get('stock.picking')._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)
