# -*- coding: utf-8 -*-
# Copyright 2014-2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoice(TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        self.account_invoice = self.env['account.invoice']
        self.account_model = self.env['account.account']
        self.account_invoice_line = self.env['account.invoice.line']
        self.analytic_account = self.env['account.analytic.account']
        self.partner_2 = self.env.ref('base.res_partner_2').id
        self.product_4 = self.env.ref('product.product_product_4').id
        self.type_receivable =\
            self.env.ref('account.data_account_type_receivable')
        self.type_expenses = self.env.ref('account.data_account_type_expenses')
        self.invoice_account = self.account_model.\
            search([('user_type_id', '=', self.type_receivable.id)], limit=1
                   ).id
        self.invoice_line_account = self.account_model.\
            search([('user_type_id', '=', self.type_expenses.id)], limit=1
                   ).id
        self.analytic_account = self.analytic_account.create({
            'name': 'Test Account',
            'code': 'TA'
        })
        self.invoice = self.account_invoice.create({
            'partner_id': self.partner_2,
            'account_id': self.invoice_account,
            'type': 'in_invoice',
        })
        self.env['account.invoice.line'].create({
            'product_id': self.product_4,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': self.invoice.id,
            'name': 'product that cost 100',
            'account_id': self.invoice_line_account,
            'account_analytic_id': self.analytic_account.id,
        })

    def test_search_analytic_accounts(self):
        self.name = self.account_invoice.\
            _search_analytic_accounts('ilike', 'Test Account')
        self.code = self.account_invoice.\
            _search_analytic_accounts('ilike', 'TA')
        self.assertEquals(self.name[0][2][0], self.code[0][2][0])
