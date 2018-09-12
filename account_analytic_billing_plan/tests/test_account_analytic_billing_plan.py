# -*- coding: utf-8 -*-
# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import exceptions


class TestAccountAnalyticBillingPlan(common.TransactionCase):

    def setUp(self):
        super(TestAccountAnalyticBillingPlan, self).setUp()
        self.billing_model = self.env['account.analytic.billing.plan']
        self.wiz_obj = self.env['wiz.create.invoice.from.billing.plan']
        self.partner = self.browse_ref('base.res_partner_address_20')
        analytic_vals = {
            'name': 'Analytic account for test billing plang',
            'type': 'normal'}
        self.analytic_account = self.env['account.analytic.account'].create(
            analytic_vals)
        billing_vals = {
            'analytic_account_id': self.analytic_account.id,
            'product_id': self.browse_ref('product.product_product_3').id,
            'amount': 5.00}
        self.billing1 = self.billing_model.create(billing_vals)
        billing_vals = {
            'analytic_account_id': self.analytic_account.id,
            'product_id': self.browse_ref('product.product_product_4').id,
            'amount': 5.00}
        self.billing2 = self.billing_model.create(billing_vals)

    def test_account_analytic_billing_plan(self):
        wiz = self.wiz_obj.create({})
        ids = [self.billing1.id, self.billing2.id]
        with self.assertRaises(exceptions.Warning):
            wiz.with_context(active_ids=ids).button_create_invoice()
        self.analytic_account.partner_id = self.partner.id
        wiz.with_context(active_ids=ids).button_create_invoice()
        self.assertNotEqual(
            self.billing1.invoice_id, False, 'Billing 1 without invoice')
        self.assertNotEqual(
            self.billing2.invoice_id, False, 'Billing 2 without invoice')
