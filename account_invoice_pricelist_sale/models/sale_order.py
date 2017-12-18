# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _prepare_invoice(self):
        """Make sure pricelist_id is set on invoice."""
        self.ensure_one()
        val = super(SaleOrder, self)._prepare_invoice()
        if self.pricelist_id:
            val.update({
                'pricelist_id': self.pricelist_id.id,
            })
        return val
