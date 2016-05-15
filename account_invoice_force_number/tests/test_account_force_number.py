# -*- coding: utf-8 -*-
# Copyright 2016 Davide Corio - davidecorio.com
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase


class TestAccountForceNumber(TransactionCase):

    def setUp(self):
        super(TestAccountForceNumber, self).setUp()

    def test_force_number(self):
        # in order to test the correct assignment of the internal_number
        # I create a customer invoice.
        invoice_vals = [
            (0, 0, {
                'product_id': self.env.ref('product.product_product_3').id,
                'quantity': 1.0,
                'account_id': self.env['account.account'].search(
                    [('user_type_id', '=', self.env.ref(
                        'account.data_account_type_revenue').id)],
                    limit=1).id,
                'name': '[PCSC234] PC Assemble SC234',
                'price_unit': 450.00
                })
        ]

        invoice = self.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': self.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': self.env.ref('base.res_partner_12').id,
            'account_id': self.env['account.account'].search(
                [('user_type_id', '=', self.env.ref(
                    'account.data_account_type_receivable').id)],
                limit=1).id,
            'invoice_line_ids': invoice_vals,
        })
        # I set the force number
        invoice.move_name = '0001'
        # I validate the invoice
        invoice.action_invoice_open()

        # I check that the invoice number is the one we expect
        self.assertEqual(invoice.number, invoice.move_name, msg='Wrong number')
