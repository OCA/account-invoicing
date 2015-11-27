# -*- coding: utf-8 -*-
# (c) 2010-2013 Savoir-faire Linux
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.osv import orm


class SaleOrder(orm.Model):

    _inherit = 'sale.order'

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):

        res = super(SaleOrder, self)._prepare_inv_line(
            cr, uid, account_id, order_line, context=context
        )
        res.update({
            'origin': order_line.order_id.name, })
        return res
