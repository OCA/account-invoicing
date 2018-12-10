# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.addons import decimal_precision


class AccountInvoiceAnalyticLineDiscount(models.Model):
    _name = 'account.invoice.analytic.line.discount'
    _description = 'Discount for analytic lines invoicing'
    _order = 'name'

    name = fields.Char(required=True)
    discount = fields.Float(
        required=True, digits=decimal_precision.get_precision('Discount'),
    )
    active = fields.Boolean(default=True)
