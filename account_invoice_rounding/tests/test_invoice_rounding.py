# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp.tests import common as test_common
from openerp.fields import Date


# @test_common.post_install(True)
class TestSwedishRounding(test_common.TransactionCase):

    def create_dummy_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'currency_id': self.env.ref('base.EUR').id,
            'account_id': self.account.id,
            'date_invoice': '%s-01-01' % self.year,
            'invoice_line': [(0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.product.id,
                'invoice_line_tax_id': [(4, self.tax_10.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 99.99,
                'journal_id': self.journal_sale.id
            })]
        })
        return invoice

    def create_dummy_invoice_2(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'currency_id': self.env.ref('base.EUR').id,
            'account_id': self.account.id,
            'date_invoice': '%s-01-01' % self.year,
            'invoice_line': [(0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.product.id,
                'invoice_line_tax_id': [(4, self.tax_77.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 90,
                'journal_id': self.journal_sale.id
            })]
        })
        return invoice

    def create_two_lines_dummy_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'currency_id': self.env.ref('base.EUR').id,
            'account_id': self.account.id,
            'date_invoice': '%s-01-01' % self.year,
            'invoice_line': [(0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.product.id,
                'invoice_line_tax_id': [(4, self.tax_10.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 99.99,
                'journal_id': self.journal_sale.id
            }), (0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.product2.id,
                'invoice_line_tax_id': [(4, self.tax_20.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 19.99,
                'journal_id': self.journal_sale.id
            })]
        })
        return invoice

    def setUp(self):
        super(TestSwedishRounding, self).setUp()
        self.year = Date.context_today(self.env.user)[:4]
        expense_type = self.env.ref('account.data_account_type_expense')
        self.journal_sale = self.env["account.journal"].create({
            "name": "Test sale journal",
            "type": "sale",
            "code": "TEST_SJ",
        })
        # expense_type.reconcile = True
        self.account = self.env['account.account'].create({
            'name': 'Rounding account',
            'code': '6666',
            'user_type': expense_type.id
        })
        tax_code_0 = self.env['account.tax.code'].create({
            'name': 'Tax0',
            'sign': 1,
        })
        tax_code_1 = self.env['account.tax.code'].create({
            'name': 'Tax1',
            'sign': 1,
        })
        tax_code_2 = self.env['account.tax.code'].create({
            'name': 'Tax2',
            'sign': 1,
        })
        self.tax_77 = self.env['account.tax'].create({
            'name': 'Dummy tax 7.7%',
            'type': 'percent',
            'amount': .077,
            'type_tax_use': 'sale',
            'tax_code_id': tax_code_0.id,
        })
        self.tax_10 = self.env['account.tax'].create({
            'name': 'Dummy tax 10%',
            'type': 'percent',
            'amount': .1,
            'type_tax_use': 'sale',
            'tax_code_id': tax_code_1.id,
        })
        self.tax_20 = self.env['account.tax'].create({
            'name': 'Dummy tax 20%',
            'type': 'percent',
            'amount': .20,
            'type_tax_use': 'sale',
            'tax_code_id': tax_code_2.id,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })
        self.product = self.env['product.product'].create({
            'name': 'Product Test',
            'list_price': 99.99,
            'default_code': 'TEST0001',
        })
        self.product2 = self.env['product.product'].create({
            'name': 'Product Test 2',
            'list_price': 19.99,
            'default_code': 'TEST0001',
        })

    def test_rounding_globally(self):
        company = self.env.ref('base.main_company')
        company.write({
            'tax_calculation_rounding_method': 'swedish_round_globally',
            'tax_calculation_rounding': 0.05,
        })
        invoice1 = self.create_dummy_invoice()
        invoice1.button_reset_taxes()
        invoice1.signal_workflow('invoice_open')
        self.assertEqual(invoice1.amount_total, 110)
        invoice2 = self.create_two_lines_dummy_invoice()
        invoice2.button_reset_taxes()
        self.assertEqual(invoice2.amount_total, 134)
        self.assertEqual(sum([t.amount for t in invoice2.tax_line]), 14.02)
        bigger_tax = self.env['account.invoice.tax'].search([
            ('invoice_id', '=', invoice2.id)], limit=1, order='amount desc')
        self.assertEqual(bigger_tax.amount, 10.02)
        self.assertEqual(len(invoice2.invoice_line), 2)
        self.assertFalse(invoice2.global_round_line_id)

    def test_rounding_per_line(self):
        company = self.env.ref('base.main_company')
        company.write({
            'tax_calculation_rounding_method': 'swedish_add_invoice_line',
            'tax_calculation_rounding': 0.05,
            'tax_calculation_rounding_account_id': self.account.id
        })
        invoice1 = self.create_dummy_invoice()
        invoice1.signal_workflow('invoice_open')
        invoice1.button_reset_taxes()
        self.assertEqual(invoice1.amount_total, 110)
        invoice2 = self.create_two_lines_dummy_invoice()
        invoice2.button_reset_taxes()
        invoice2.signal_workflow('invoice_open')
        self.assertEqual(invoice2.amount_total, 134)
        self.assertEqual(sum([t.amount for t in invoice2.tax_line]), 14)
        self.assertEqual(len(invoice2.invoice_line), 3)
        self.assertEqual(invoice2.global_round_line_id.price_subtotal, 0.02)

        # test with pressing taxes reset button before validation
        invoice3 = self.create_dummy_invoice_2()
        invoice3.button_reset_taxes()
        invoice3.signal_workflow('invoice_open')
        self.assertEqual(invoice3.amount_total, 96.95)
        self.assertEqual(invoice3.amount_untaxed, 90.02)

        # test without pressing taxes reset button before validation
        invoice3 = self.create_dummy_invoice_2()
        invoice3.signal_workflow('invoice_open')
        self.assertEqual(invoice3.amount_total, 96.95)
        self.assertEqual(invoice3.amount_untaxed, 90.02)
