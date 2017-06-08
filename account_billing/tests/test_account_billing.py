# -*- coding: utf-8 -*-
#
#    Author: Kitti Upariphutthiphong
#    Copyright 2014-2015 Ecosoft Co., Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import time
import openerp.tests.common as common


class TestAccountBilling(common.TransactionCase):

    def setUp(self):
        """
        Create 1st invoice, 100 THB, dated 15 this month
        Create 2nd invoice, 200 THB, dated 20 this month
        Confirm both invoices
        """
        super(TestAccountBilling, self).setUp()
        # Model
        self.billing_obj = self.env['account.billing']
        self.billing_line_obj = self.env['account.billing.line']
        self.invoice_obj = self.env['account.invoice']
        self.voucher_obj = self.env['account.voucher']
        # Master Data
        self.company_id = self.env.user.company_id.id
        self.partner_id = self.ref('base.res_partner_3')  # China Export
        self.product_id = \
            self.ref('product.product_product_25_product_template')
        self.thb_currency_id = self.ref('base.THB')
        self.eur_currency_id = self.ref('base.EUR')
        self.date_15 = time.strftime('%Y-%m') + '-15'
        self.date_17 = time.strftime('%Y-%m') + '-15'
        self.date_20 = time.strftime('%Y-%m') + '-20'
        self.date_25 = time.strftime('%Y-%m') + '-25'
        # get account_id
        self.account_id = self.invoice_obj.onchange_partner_id(
            'out_invoice', self.partner_id,
            date_invoice=self.date_15)['value']['account_id']
        # create invoice#1 (dated 15)
        self.invoice1 = self.invoice_obj.create({
            'partner_id': self.partner_id,
            'account_id': self.account_id,
            'currency_id': self.thb_currency_id,
            'date_invoice': self.date_15,
            'invoice_line': [(0, 0, {
                'product_id': self.product_id,
                'name': 'Sample Product',
                'quantity': 1,
                'price_unit': 100,
                'invoice_line_tax_id': [],
            })]
        })
        # create invoice#1 (dated 20)
        self.invoice2 = self.invoice_obj.create({
            'partner_id': self.partner_id,
            'account_id': self.account_id,
            'currency_id': self.thb_currency_id,
            'date_invoice': self.date_20,
            'invoice_line': [(0, 0, {
                'product_id': self.product_id,
                'name': 'Sample Product',
                'quantity': 1,
                'price_unit': 200,
                'invoice_line_tax_id': [],
            })]
        })
        # confirm invoices
        self.invoice1.signal_workflow('invoice_open')
        self.invoice2.signal_workflow('invoice_open')

    def test_normal_case(self):
        """
        Create billing document dated 17, THB
        Check that billing amount = 1st invoice only
        Confirm Billing and use it in Payment
        """
        # create billing dated 17
        billing = self.billing_obj.create({
            'partner_id': self.partner_id,
            'date': self.date_17,
            'currency_id': self.thb_currency_id,
        })
        billing_line_dict = self.billing_obj.onchange_partner_id(
            self.company_id,
            self.partner_id,
            self.thb_currency_id,
            self.date_17)['value']['line_cr_ids']
        for line in billing_line_dict:
            line.update({'billing_id': billing.id})
            self.billing_line_obj.create(line)
        # found only invoice 1
        self.assertEquals(billing.billing_amount, 100.0)
        # validate billing
        billing.validate_billing()
        # create payment voucher on 25 but use billing
        journal_id = self.voucher_obj._get_journal()
        res = self.voucher_obj.onchange_billing_id(
            self.partner_id, journal_id, 0.0,
            self.eur_currency_id, 'receipt', self.date_25)
        # still match 2 invoice
        self.assertEquals(len(res['value']['line_cr_ids']), 2)

        res = self.voucher_obj.with_context(
            billing_id=billing.id).onchange_billing_id(
                self.partner_id, journal_id, 0.0,
                self.eur_currency_id, 'receipt', self.date_25)
        # billing assigned, match 1 invoice
        self.assertEquals(len(res['value']['line_cr_ids']), 1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
