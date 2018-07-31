# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        """Set pricelist from sale.order if set on picking."""
        inv_vals = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move
        )
        sale = move.picking_id.sale_id
        if sale and sale.pricelist_id:
            inv_vals.update({
                'pricelist_id': sale.pricelist_id.id,
            })
        return inv_vals
