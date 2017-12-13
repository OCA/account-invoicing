# -*- coding: utf-8 -*-
# Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
# Author: Nicola Malcontenti <nicola.malcontenti@agilebg.com>
# Copyright 2017 Apulia Software srl - www.apuliasoftware.it
# Author Andrea Cometa <a.cometa@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        invoice_vals = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        if move and move.partner_id:
            # this field is provided by stock_transport_multi_address module
            if 'delivery_address_id' in self.pool['stock.picking']._fields:
                invoice_vals['address_shipping_id'] = \
                    move.picking_id.delivery_address_id.id
            else:
                invoice_vals[
                    'address_shipping_id'] = move.picking_id.partner_id.id
        return invoice_vals
