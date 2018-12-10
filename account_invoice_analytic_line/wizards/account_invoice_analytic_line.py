# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountAnalyticLineInvoice(models.TransientModel):
    _name = 'account.analytic.line.invoice'
    _description = 'Invoice analytic lines wizard'

    @api.multi
    def action_invoice(self):
        return self.env['account.analytic.line'].browse(
            self.env.context.get('active_ids')
        )._account_invoice_analytic_line()
