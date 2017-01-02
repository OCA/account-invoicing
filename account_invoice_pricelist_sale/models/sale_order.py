# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_invoice(self, order, lines):
        """Make sure pricelist_id is set on invoice."""
        val = super(SaleOrder, self)._prepare_invoice(order, lines)
        if order.pricelist_id:
            val.update({
                'pricelist_id': order.pricelist_id.id,
            })
        return val
