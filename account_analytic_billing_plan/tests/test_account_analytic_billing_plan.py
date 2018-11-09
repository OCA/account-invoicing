# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common
from odoo.exceptions import UserError


class TestAccountAnalyticBillingPlan(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticBillingPlan, cls).setUpClass()
        cls.billing_model = cls.env['account.analytic.billing.plan']
        partner_model = cls.env['res.partner']
        analytic_model = cls.env['account.analytic.account']
        product_model = cls.env['product.product']
        fiscal_position = cls.env['account.fiscal.position'].create({
            'name': 'Fiscal Position',
        })
        cls.partner = partner_model.create({
            'name': 'New Partner 1',
            'property_account_position_id': fiscal_position.id,
        })
        cls.analytic = analytic_model.create({
            'name': 'New Analytic Account',
            'partner_id': cls.partner.id,
        })
        cls.product1 = product_model.create({
            'name': 'New Product 1',
            'lst_price': 10.0,
        })
        cls.product2 = product_model.create({
            'name': 'New Product 2',
            'lst_price': 50.0,
        })
        cls.plan1 = cls.billing_model.create({
            'analytic_account_id': cls.analytic.id,
            'product_id': cls.product1.id,
            'amount': cls.product1.lst_price,
        })
        cls.plan2 = cls.billing_model.create({
            'analytic_account_id': cls.analytic.id,
            'product_id': cls.product2.id,
            'amount': cls.product2.lst_price,
        })

    def test_billing_plan(self):
        self.assertFalse(self.plan1.invoice_id)
        self.plan1.action_invoice_create()
        self.assertTrue(self.plan1.invoice_id)
        with self.assertRaises(UserError):
            self.plan1.action_invoice_create()

    def test_billing_plans(self):
        plans = self.plan1 | self.plan2
        plans.action_invoice_create()
        self.assertEqual(self.plan1.invoice_id, self.plan2.invoice_id)

    def test_billing_plans_twopartner(self):
        partner = self.partner.copy()
        analytic = self.analytic.copy(default={'partner_id': partner.id})
        self.assertFalse(analytic.billing_plan_count)
        self.plan2.analytic_account_id = analytic
        analytic.invalidate_cache()
        self.assertEqual(analytic.billing_plan_count, 1)
        plans = self.plan1 | self.plan2
        plans.action_invoice_create()
        self.assertNotEqual(self.plan1.invoice_id, self.plan2.invoice_id)

    def test_billing_plan_onchange(self):
        plan = self.billing_model.new({
            'analytic_account_id': self.analytic.id,
            'product_id': self.product2.id
        })
        plan._onchange_product_id()
        self.assertEqual(plan.amount, self.product2.lst_price)

    def test_billing_plan_open(self):
        self.assertEqual(self.analytic.billing_plan_count, 2)
        action_dict = self.analytic.button_open_billing_plan()
        self.assertEqual(
            action_dict.get('res_model'), 'account.analytic.billing.plan')

    def test_billing_plan_invoice_user_error(self):
        self.env['account.journal'].search([]).write({'active': False})
        with self.assertRaises(UserError):
            self.plan1.action_invoice_create()

    def test_billing_plan_invoice_line_user_error(self):
        self.plan1.product_id.categ_id.property_account_income_categ_id = False
        self.plan1.product_id.property_account_income_id = False
        with self.assertRaises(UserError):
            self.plan1.action_invoice_create()
