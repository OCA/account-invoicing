# -*- coding: utf-8 -*-
# Copyright 2014-2015 Agile Business Group sagl
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    incoterm = fields.Many2one(
        comodel_name='stock.incoterms',
        string='Incoterm',
        help="International Commercial Terms are a series of predefined "
        "commercial terms used in international transactions.",
    )

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        invoice_vals = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        if move.picking_id.incoterm:
            invoice_vals['incoterm'] = move.picking_id.incoterm.id
        return invoice_vals
