# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import openerp.tests.common as test_common


class TestSwedishRounding(test_common.TransactionCase):

    def create_dummy_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'currency_id': self.env.ref('base.EUR').id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Dummy invoice line',
                'product_id': self.product.id,
                'invoice_line_tax_ids': [(4, self.tax.id)],
                'account_id': self.account.id,
                'quantity': 1,
                'price_unit': 99.99,
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
        self.product = self.env['product.product'].create({
            'name': 'Dummy product',
            'type': 'consu',
            'lst_price': 6.67
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Dummy Partner',
            'customer': True
        })
        self.tax = self.env['account.tax'].create({
            'name': 'Dummy tax 10%',
            'amount_type': 'percent',
            'amount': 10.0000,
            'type_tax_use': 'sale',
        })

    def test_rounding_globally(self):
        company = self.env.ref('base.main_company')
        company.write({
            'tax_calculation_rounding_method': 'swedish_round_globally',
            'tax_calculation_rounding': 0.05,
        })
        invoice = self.create_dummy_invoice()
        self.assertEqual(invoice.amount_total, 110)

    def test_rounding_per_line(self):
        company = self.env.ref('base.main_company')
        company.write({
            'tax_calculation_rounding_method': 'swedish_add_invoice_line',
            'tax_calculation_rounding': 0.05,
            'tax_calculation_rounding_account_id': self.account.id
        })
        invoice = self.create_dummy_invoice()
        self.assertEqual(invoice.amount_total, 110)
