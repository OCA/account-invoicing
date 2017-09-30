# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError

import time


class TestAccountInvoice(TransactionCase):

    descriptions = ['a description', 'b description', 'c description']

    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.account_model = self.env['account.account']
        self.partner = self.browse_ref("base.res_partner_2")

        self.account_customer = self.account_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1).id
        self.account_line = self.env['account.account'].search([
            ('user_type_id',
             '=',
             self.env.ref('account.data_account_type_revenue').id
             )], limit=1).id

        self.lines_vals1 = [
            {'quantity': 3,
             'price_unit': 100,
             'name': self.descriptions[0],
             'account_id':  self.account_line,
             'sequence': 1},
            {'quantity': 4,
             'price_unit': 99,
             'name': self.descriptions[1],
             'account_id': self.account_line,
             'sequence': 2},
            {'quantity': 2,
             'price_unit': 120,
             'account_id': self.account_line,
             'name': self.descriptions[2],
             'sequence': 3}
        ]
        self.invoice_vals1 = {
            'partner_id': self.partner.id,
            'name': 'ref1',
            'account_id':  self.account_customer,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-07-01',
            'invoice_line_ids': [(0, 0, value) for value in self.lines_vals1]
        }

        self.lines_vals2 = [
            {'quantity': 3,
             'price_unit': 100,
             'name': self.descriptions[0],
             'account_id': self.account_line,
             'sequence': 1},
            {'quantity': 4,
             'price_unit': 99,
             'name': self.descriptions[1],
             'account_id': self.account_line,
             'sequence': 2},
            {'quantity': 2,
             'price_unit': 120,
             'name': self.descriptions[2],
             'account_id': self.account_line,
             'sequence': 3}
        ]
        self.invoice_vals2 = {
            'partner_id': self.partner.id,
            'name': 'ref1',
            'account_id': self.account_customer,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-07-01',
            'invoice_line_ids': [(0, 0, value) for value in self.lines_vals2]
        }

    def test_action_duplicate_invoice(self):
        # Creation of  invoice instances with de same customer and reference
        # Result: ValidationError
        with self.assertRaises(IntegrityError):
            self.invoice_model.create(self.invoice_vals1)
            self.invoice_model.create(self.invoice_vals2)
