# -*- coding: utf-8 -*-
# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    billing_plan_ids = fields.One2many(
        comodel_name='account.analytic.billing.plan',
        inverse_name='analytic_account_id', string='Billing plans')

    def create_invoice_from_billing_plans(self, plans):
        customers = {}
        for plan in plans:
            if not customers.get(plan.analytic_account_id.name, False):
                customers[plan.analytic_account_id.name] = (
                    self.create_invoice_from_billing_plan(plan))
            invoice = customers.get(plan.analytic_account_id.name)
            plan.invoice_id = invoice.id
            self.create_invoice_line_from_billing_plan(invoice, plan)

    @api.multi
    def create_invoice_from_billing_plan(self, plan):
        invoice_vals = self.get_invoice_vals_for_billing_plan(plan)
        invoice = self.create(invoice_vals)
        return invoice

    @api.multi
    def get_invoice_vals_for_billing_plan(self, plan):
        result = self.onchange_partner_id(
            'out_invoice', plan.partner_id.id,
            company_id=self.env.user.company_id.id)
        value = result.get('value')
        invoice_vals = {
            'partner_id': plan.partner_id.id,
            'type': 'out_invoice'}
        invoice_vals.update({
            'fiscal_position': value.get('fiscal_position', False),
            'date_due': value.get('date_due', False),
            'account_id': value.get('account_id', False),
            'payment_term': value.get('payment_term', False)})
        return invoice_vals

    @api.multi
    def create_invoice_line_from_billing_plan(self, invoice, plan):
        values = self.get_invoice_line_vals_for_billing_plan(invoice, plan)
        values.update({
            'product_id': plan.product_id.id,
            'invoice_id': invoice.id,
            'price_unit': plan.amount,
            'invoice_line_tax_id':
            [(6, 0, values.get('invoice_line_tax_id', []))]})
        line = self.env['account.invoice.line'].create(values)
        return line

    @api.multi
    def get_invoice_line_vals_for_billing_plan(self, invoice, plan):
        fposition = (
            invoice.fiscal_position.id if invoice.fiscal_position else False)
        result = self.env['account.invoice.line'].product_id_change(
            plan.product_id.id, plan.product_id.uom_id.id, qty=1,
            partner_id=plan.partner_id.id, fposition_id=fposition,
            price_unit=plan.amount, currency_id=invoice.currency_id.id,
            company_id=invoice.company_id.id)
        return result.get('value')
