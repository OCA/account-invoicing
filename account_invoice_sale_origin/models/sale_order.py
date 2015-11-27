# -*- coding: utf-8 -*-
# © 2010-2013 Savoir-faire Linux
# © 2015 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
