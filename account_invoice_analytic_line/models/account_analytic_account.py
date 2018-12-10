# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    account_invoice_analytic_line_product_id = fields.Many2one(
        'product.product', string='Invoice product',
        help='This product will be used to invoice analytic lines',
    )
