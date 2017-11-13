# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountPaymentTerm(TransactionCase):

    def setUp(self):
        super(TestAccountPaymentTerm, self).setUp()
        self.account_payment_term = self.env['account.payment.term']
        self.sixty_days_end_of_month = self.env.ref(
            'account_payment_term_extension.sixty_days_end_of_month')

    def test_00_compute(self):
        res = self.sixty_days_end_of_month.compute(
            10, date_ref='2015-01-30')
        self.assertEquals(
            res[0][0][0],
            '2015-03-31',
            'Error in the compute of payment terms with months')

    def test_01_compute(self):
        two_week_payterm = self.account_payment_term.create({
            'name': '2 weeks',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'days': 0,
                'weeks': 2,
                'option': 'day_after_invoice_date'})]
            })
        res = two_week_payterm.compute(10, date_ref='2015-03-02')
        self.assertEquals(
            res[0][0][0],
            '2015-03-16',
            'Error in the compute of payment terms with weeks')
