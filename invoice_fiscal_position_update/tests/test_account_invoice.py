# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase

import time


class TestAccountInvoice(TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        self.fiscal_position_model = self.env['account.fiscal.position']
        self.tax_model = self.env['account.tax']
        self.product_model = self.env['product.product']
        self.account_invoice_model = self.env['account.invoice']
        self.account_invoice_line_model = self.env['account.invoice.line']
        self.partner = self.browse_ref("base.res_partner_2")
        self.account_model = self.env['account.account']
        account_user_type = self.env.ref(
            'account.data_account_type_receivable')
        self.account_rcv = self.account_model.create({
            'code': "cust_acc",
            'name': "customer account",
            'user_type_id': account_user_type.id,
            'reconcile': True,
        })
        self.test_tax = self.tax_model.create({
            'name': "Test tax",
            'amount_type': 'fixed',
            'amount': 10,
            'sequence': 1,
        })
        self.test_tax_bis = self.tax_model.create({
            'name': "Test tax bis",
            'amount_type': 'fixed',
            'amount': 15,
            'sequence': 2,
        })
        self.product = self.product_model.create({
            'name': "Voiture",
            'list_price': '121',
            'taxes_id': [(6, 0, [self.test_tax.id])],
            'standard_price': 10
        })
        tax_vals = {
            'tax_src_id': self.test_tax.id,
            'tax_dest_id': self.test_tax_bis.id
        }
        self.fiscal_position = self.fiscal_position_model.create({
            'name': 'Test Fiscal Position',
            'tax_ids': [(0, 0, tax_vals)]
        })

        self.invoice = self.account_invoice_model.create({
            'partner_id': self.partner.id,
            'fiscal_position_id': False,
            'name': 'invoice to client',
            'account_id': self.account_rcv.id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-07-01'
        })
        self.account_revenue = self.env['account.account'].search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_revenue').id)],
            limit=1)
        self.invoice_line = self.account_invoice_line_model.create({
            'invoice_id': self.invoice.id,
            'quantity': 3,
            'price_unit': 100,
            'name': 'Test Line',
            'sequence': 1,
            'product_id': self.product.id,
            'account_id': self.account_revenue.id,
        })

        self.invoice_line._onchange_product_id()

    def test_update_fiscal_position(self):
        self.assertEquals(
            self.invoice_line.invoice_line_tax_ids.id,
            self.test_tax.id
        )
        self.invoice.fiscal_position_id = self.fiscal_position
        self.invoice.onchange_fiscal_position_id()
        self.assertEquals(
            self.invoice_line.invoice_line_tax_ids.id,
            self.test_tax_bis.id
        )
