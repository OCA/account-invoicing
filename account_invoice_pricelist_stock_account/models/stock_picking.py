# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        """Set pricelist from sale / purchase order if set on picking."""
        inv_vals = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move
        )
        pricelist_id = False
        picking = move.picking_id
        if inv_type in ['out_invoice', 'out_refund']:
            # Get the pricelist of the sale order, if defined
            if self._model._columns.get('sale_id', False):
                pricelist_id = picking.sale_id.pricelist_id.id

        elif inv_type in ['in_invoice', 'in_refund']:
            # Get the pricelist of the purchase order, if defined
            if move._model._columns.get('purchase_line_id', False):
                pricelist_id = move.purchase_line_id.order_id.pricelist_id.id

        if not pricelist_id and picking.partner_id:
            # Set the default pricelist of the partner
            pricelist_id = picking.partner_id._get_invoice_pricelist_id(
                inv_type)

        inv_vals['pricelist_id'] = pricelist_id

        return inv_vals
