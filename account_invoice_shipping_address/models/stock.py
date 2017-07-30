# -*- coding: utf-8 -*-

from openerp import models,fields

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_invoice_vals(self,inv_type,
                          journal_id, picking,):
        invoice_vals = super(StockPicking, self)._get_invoice_vals(
            inv_type, journal_id, picking)
        if picking and picking.partner_id:
            invoice_vals['address_shipping_id'] = picking.partner_id.id
        return invoice_vals
