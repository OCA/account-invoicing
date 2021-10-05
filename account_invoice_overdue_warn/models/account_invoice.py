# -*- coding: utf-8 -*-
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    residual_company_currency = fields.Float(
        compute='_compute_residual_company_currency',
        digits=dp.get_precision('Account'),
        string='Residual in Company Currency', store=True,
        help='The amount is negative for a refund')

    @api.one
    @api.depends(
        'currency_id', 'move_id', 'date_invoice', 'type', 'company_id',
        'residual')
    def _compute_residual_company_currency(self):
        # Convert on the date of the invoice
        sign = 1
        if self.type in ('out_refund', 'in_refund'):
            sign = -1
        self.residual_company_currency = self.currency_id.with_context(
            date=self.date_invoice, disable_rate_date_check=True).compute(
                self.residual, self.company_id.currency_id) * sign
