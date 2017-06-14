# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import openerp.tests.common as test_common


class TestSwedishRounding(test_common.TransactionCase):

    def create_dummy_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'currency_id': self.env.ref('base.EUR').id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.env.ref('product.product_product_1').id,
                'invoice_line_tax_ids': [(4, self.tax_10.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 99.99,
            })]
        })
        return invoice

    def create_two_lines_dummy_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'currency_id': self.env.ref('base.EUR').id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.env.ref('product.product_product_1').id,
                'invoice_line_tax_ids': [(4, self.tax_10.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 99.99,
            }), (0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.env.ref('product.product_product_2').id,
                'invoice_line_tax_ids': [(4, self.tax_20.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 19.99,
            })]
        })
        return invoice

    def setUp(self):
        super(TestSwedishRounding, self).setUp()
        # self.sudo(self.ref('base.user_demo'))
        expense_type = self.env.ref('account.data_account_type_depreciation')
        expense_type.reconcile = True
        self.account = self.env['account.account'].create({
            'name': 'Rounding account',
            'code': '6666',
            'user_type_id': expense_type.id
        })
        self.tax_10 = self.env['account.tax'].create({
            'name': 'Dummy tax 10%',
            'amount_type': 'percent',
            'amount': 10.0000,
            'type_tax_use': 'sale',
        })
        self.tax_20 = self.env['account.tax'].create({
            'name': 'Dummy tax 20%',
            'amount_type': 'percent',
            'amount': 20.0000,
            'type_tax_use': 'sale',
        })

    def test_rounding_globally(self):
        company = self.env.ref('base.main_company')
        company.write({
            'tax_calculation_rounding_method': 'swedish_round_globally',
            'tax_calculation_rounding': 0.05,
        })
        invoice1 = self.create_dummy_invoice()
        self.assertEqual(invoice1.amount_total, 110)
        invoice2 = self.create_two_lines_dummy_invoice()
        self.assertEqual(invoice2.amount_total, 134)
        self.assertEqual(sum([t.amount for t in invoice2.tax_line_ids]), 14.02)
        bigger_tax = self.env['account.invoice.tax'].search([
            ('invoice_id', '=', invoice2.id)], limit=1, order='amount desc')
        self.assertEqual(bigger_tax.amount, 10.02)
        self.assertEqual(len(invoice2.invoice_line_ids), 2)
        self.assertFalse(invoice2.global_round_line_id)

    def test_rounding_per_line(self):
        company = self.env.ref('base.main_company')
        company.write({
            'tax_calculation_rounding_method': 'swedish_add_invoice_line',
            'tax_calculation_rounding': 0.05,
            'tax_calculation_rounding_account_id': self.account.id
        })
        invoice1 = self.create_dummy_invoice()
        self.assertEqual(invoice1.amount_total, 110)
        invoice2 = self.create_two_lines_dummy_invoice()
        self.assertEqual(invoice2.amount_total, 134)
        self.assertEqual(sum([t.amount for t in invoice2.tax_line_ids]), 14)
        self.assertEqual(len(invoice2.invoice_line_ids), 3)
        self.assertEqual(invoice2.global_round_line_id.price_subtotal, 0.02)
