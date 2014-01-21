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

from openerp.osv import orm


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    def product_id_change(
        self, cr, uid, ids, product_id, uom_id, qty=0,
        name='', type='out_invoice', partner_id=False, fposition_id=False,
        price_unit=False, currency_id=False, context=None, company_id=None
    ):
        res = super(account_invoice_line, self).product_id_change(
            cr, uid, ids, product_id, uom_id, qty=qty,
            name=name, type=type, partner_id=partner_id,
            fposition_id=fposition_id, price_unit=price_unit,
            currency_id=currency_id, context=context, company_id=company_id
        )
        if product_id:
            user = self.pool.get('res.users').browse(
                cr, uid, uid, context=context)
            user_groups = [g.id for g in user.groups_id]
            ref = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'invoice_line_description',
                'group_use_product_description_per_inv_line'
            )
            if ref and len(ref) > 1 and ref[1]:
                group_id = ref[1]
                if group_id in user_groups:
                    product_obj = self.pool.get('product.product')
                    product = product_obj.browse(
                        cr, uid, product_id, context=context)
                    if (
                        product
                        and product.description
                        and 'value' in res
                    ):
                        res['value']['name'] = product.description
        return res
