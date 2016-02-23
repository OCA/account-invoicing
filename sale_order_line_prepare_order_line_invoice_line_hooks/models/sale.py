# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jordi Ballester (Eficent)
#    Copyright 2015 Eficent
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
from openerp.osv import osv


class SaleOrderLine(osv.osv):
    _inherit = "sale.order.line"

    def _prepare_order_line_invoice_line_hook(self, cr, uid, line,
                                              account_id=False, context=None):

        if not account_id:
            if line.product_id:
                account_id = line.product_id.property_account_income.id
                if not account_id:
                    account_id = line.product_id.\
                        categ_id.property_account_income_categ.id
                if not account_id:
                    raise osv.except_osv(
                        _('Error!'),
                        _('Please define income account '
                          'for this product: "%s" (id:%d).') %
                        (line.product_id.name, line.product_id.id,))
            else:
                prop = self.pool.get('ir.property').get(
                    cr, uid, 'property_account_income_categ',
                    'product.category', context=context)
                account_id = prop and prop.id or False
        uosqty = self._get_line_qty(cr, uid, line, context=context)
        uos_id = self._get_line_uom(cr, uid, line, context=context)
        pu = 0.0
        if uosqty:
            pu = round(line.price_unit * line.product_uom_qty / uosqty,
                       self.pool.get('decimal.precision').precision_get(
                            cr, uid, 'Product Price'))
        fpos = line.order_id.fiscal_position or False
        account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
        if not account_id:
            raise osv.except_osv(
                _('Error!'),
                _('There is no Fiscal Position defined or '
                  'Income category account defined for '
                  'default properties of Product categories.'))
        res = {
            'name': line.name,
            'sequence': line.sequence,
            'origin': line.order_id.name,
            'account_id': account_id,
            'price_unit': pu,
            'quantity': uosqty,
            'discount': line.discount,
            'uos_id': uos_id,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
            'account_analytic_id': (line.order_id.project_id and
                                    line.order_id.project_id.id or False),
        }
        return res

    def _prepare_order_line_invoice_line(self, cr, uid, line,
                                         account_id=False, context=None):
        """ Add Hook """
        res = {}
        if not line.invoiced:
            # HOOK
            res = self._prepare_order_line_invoice_line_hook(
                cr, uid, line, account_id=account_id, context=context)
            # --
        return res
