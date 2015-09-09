# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    related_picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        relation='account_invoice_stock_picking_rel',
        column1='account_invoice_id',
        column2='stock_picking_id',
        string='Related Pickings',
        readonly=True,
        copy=False,
        help='Related pickings '
             '(only when the invoice has been generated from the picking).'
    )
