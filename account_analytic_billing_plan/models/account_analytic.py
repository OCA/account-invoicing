# -*- coding: utf-8 -*-
# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    billing_plan_ids = fields.One2many(
        comodel_name='account.analytic.billing.plan',
        inverse_name='analytic_account_id', string='Billing plans')


class AccountAnalyticBillingPlan(models.Model):
    _name = 'account.analytic.billing.plan'
    _description = 'Billing plan'
    _rec_name = 'product_id'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic account',
        required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner', store=True,
        related='analytic_account_id.partner_id')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    amount = fields.Float(
        string='Amount', digits=dp.get_precision('Account'), required=True)
    estimated_billing_date = fields.Date(
        string='Estimated billing date')
    invoice_id = fields.Many2one(
        comodel_name='account.invoice', string='Invoice')
    invoice_state = fields.Selection(
        string='Invoice state', related='invoice_id.state', store=True)

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        for plan in self.filtered('product_id'):
            plan.amount = plan.product_id.lst_price
