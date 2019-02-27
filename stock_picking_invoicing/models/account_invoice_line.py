# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    stock_move_ids = fields.Many2many(
        comodel_name='stock.move',
        relation="stock_move_account_move_line_m2m",
        column1="invoice_line_id",
        column2="stock_move_id",
        string='Stock moves',
        readonly=True,
    )
