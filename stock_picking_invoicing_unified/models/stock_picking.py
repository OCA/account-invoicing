# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona <ainaragaldona@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(move, partner,
                                                            inv_type)
        # negative value on quantity
        if ((inv_type == 'out_invoice' and
                move.location_id.usage == 'customer') or
                (inv_type == 'out_refund' and
                 move.location_dest_id.usage == 'customer') or
                (inv_type == 'in_invoice' and
                 move.location_dest_id.usage == 'supplier') or
                (inv_type == 'in_refund' and
                 move.location_id.usage == 'supplier')):
            res['quantity'] *= -1
        return res
