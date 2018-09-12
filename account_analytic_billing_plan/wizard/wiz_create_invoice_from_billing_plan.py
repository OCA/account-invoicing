# -*- coding: utf-8 -*-
# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _


class WizCreateInvoiceFromBillingPlan(models.TransientModel):
    _name = 'wiz.create.invoice.from.billing.plan'

    name = fields.Char(string='Description')

    @api.multi
    def button_create_invoice(self):
        self.ensure_one()
        plan_obj = self.env['account.analytic.billing.plan']
        plans = plan_obj.browse(self.env.context.get('active_ids')).filtered(
            lambda x: not x.invoice_id)
        error = ""
        for plan in plans.filtered(lambda x: not x.partner_id):
            lit = _(u"Billing plan for product: {}, with analytic account: {},"
                    " without partner.\n")
            error += lit.format(
                plan.product_id.name, plan.analytic_account_id.name)
        if error:
            raise exceptions.Warning(error)
        self.env['account.invoice'].create_invoice_from_billing_plans(plans)
