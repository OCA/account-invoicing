# -*- coding: utf-8 -*-
##############################################################################

#     This file is part of account_invoice_line_sort, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_line_sort is free software: you can redistribute it
#     and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     account_invoice_line_sort is distributed in the hope that it will
#     be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with account_invoice_line_sort.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase
import time


class test_account_invoice_line_sort(object):

    _module_ns = 'account_invoice_line_sort'

    descriptions = ['a description', 'b description', 'c description']

    def setUp(self):
        super(test_account_invoice_line_sort, self).setUp()
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.account_rcv_id = self.ref("account.a_recv")
        self.partner = self.browse_ref("base.res_partner_2")
        self.lines_vals = [
            {'quantity': 3,
             'price_unit': 100,
             'name': self.descriptions[0],
             'sequence': 1},
            {'quantity': 4,
             'price_unit': 99,
             'name': self.descriptions[1],
             'sequence': 2},
            {'quantity': 2,
             'price_unit': 120,
             'name': self.descriptions[2],
             'sequence': 3}
        ]
        self.invoice_vals = {
            'partner_id': self.partner.id,
            'name': 'invoice to client',
            'account_id': self.account_rcv_id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-07-01',
            'invoice_line': [(0, 0, value) for value in self.lines_vals]
        }

    def test_invoice_sort_on_create(self):
        self.partner.line_order = self.line_order
        self.partner.line_order_direction = self.line_order_direction

        invoice = self.invoice_model.create(self.invoice_vals)

        for line in invoice.invoice_line:
            self.assertEqual(line.sequence,
                             self.expected_sequence[line.name],
                             'Sequence should be %s and not %s !' %
                             (self.expected_sequence[line.name],
                              line.sequence))

    def test_invoice_sort_on_write(self):
        invoice = self.invoice_model.create(self.invoice_vals)
        invoice.line_order = self.line_order
        invoice.line_order_direction = self.line_order_direction

        for line in invoice.invoice_line:
            self.assertEqual(line.sequence,
                             self.expected_sequence[line.name],
                             'Sequence should be %s and not %s !' %
                             (self.expected_sequence[line.name],
                              line.sequence))


class test_account_invoice_line_sort_name_asc(test_account_invoice_line_sort,
                                              SharedSetupTransactionCase):

        def setUp(self):
            super(test_account_invoice_line_sort_name_asc, self).setUp()
            self.expected_sequence = {self.descriptions[0]: 10,
                                      self.descriptions[1]: 20,
                                      self.descriptions[2]: 30}
            self.line_order = 'name'
            self.line_order_direction = 'asc'


class test_account_invoice_line_sort_name_desc(test_account_invoice_line_sort,
                                               SharedSetupTransactionCase):

        def setUp(self):
            super(test_account_invoice_line_sort_name_desc, self).setUp()
            self.expected_sequence = {self.descriptions[0]: 30,
                                      self.descriptions[1]: 20,
                                      self.descriptions[2]: 10}
            self.line_order = 'name'
            self.line_order_direction = 'desc'


class test_account_invoice_line_sort_price_unit_asc(
        test_account_invoice_line_sort, SharedSetupTransactionCase):

        def setUp(self):
            super(test_account_invoice_line_sort_price_unit_asc, self).setUp()
            self.expected_sequence = {self.descriptions[0]: 20,
                                      self.descriptions[1]: 10,
                                      self.descriptions[2]: 30}
            self.line_order = 'price_unit'
            self.line_order_direction = 'asc'


class test_account_invoice_line_sort_price_unit_desc(
        test_account_invoice_line_sort, SharedSetupTransactionCase):

        def setUp(self):
            super(test_account_invoice_line_sort_price_unit_desc, self).setUp()
            self.expected_sequence = {self.descriptions[0]: 20,
                                      self.descriptions[1]: 30,
                                      self.descriptions[2]: 10}
            self.line_order = 'price_unit'
            self.line_order_direction = 'desc'


class test_account_invoice_line_sort_amount_asc(
        test_account_invoice_line_sort, SharedSetupTransactionCase):

        def setUp(self):
            super(test_account_invoice_line_sort_amount_asc, self).setUp()
            self.expected_sequence = {self.descriptions[0]: 20,
                                      self.descriptions[1]: 30,
                                      self.descriptions[2]: 10}
            self.line_order = 'price_subtotal'
            self.line_order_direction = 'asc'


class test_account_invoice_line_sort_amount_desc(
        test_account_invoice_line_sort, SharedSetupTransactionCase):

        def setUp(self):
            super(test_account_invoice_line_sort_amount_desc, self).setUp()
            self.expected_sequence = {self.descriptions[0]: 20,
                                      self.descriptions[1]: 10,
                                      self.descriptions[2]: 30}
            self.line_order = 'price_subtotal'
            self.line_order_direction = 'desc'
