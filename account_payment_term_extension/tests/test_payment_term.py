# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
##############################################################################

from openerp.tests.common import TransactionCase


class TestAccountPaymentTerm(TransactionCase):

    def setUp(self):
        super(TestAccountPaymentTerm, self).setUp()
        self.account_payment_term = self.registry('account.payment.term')
        self.sixty_days_end_of_month =\
            self.registry('ir.model.data').xmlid_to_res_id(
                self.cr, self.uid,
                'account_payment_term_extension.sixty_days_end_of_month')

    def test_00_compute(self):
        cr, uid = self.cr, self.uid
        res = self.account_payment_term.compute(
            cr, uid, self.sixty_days_end_of_month, 10, date_ref='2015-01-30')
        self.assertEquals(
            res[0][0],
            '2015-03-31',
            'Error in the compute of payment terms with months')

    def test_01_compute(self):
        cr, uid = self.cr, self.uid
        two_week_payterm_id = self.account_payment_term.create(
            cr, uid, {
            'name': '2 weeks',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'days': 0,
                'weeks': 2})]
            })
        res = self.account_payment_term.compute(
            cr, uid, two_week_payterm_id, 10, date_ref='2015-03-02')
        self.assertEquals(
            res[0][0],
            '2015-03-16',
            'Error in the compute of payment terms with weeks')
