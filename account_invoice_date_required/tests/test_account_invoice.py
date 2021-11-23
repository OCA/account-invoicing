# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestAccountInvoice(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        self.account_invoice = self.env['account.invoice']
        self.account_model = self.env['account.account']
        self.account_invoice_line = self.env['account.invoice.line']
        self.current_user = self.env.user

        self.invoice_account = self.account_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1)
        # Instance: Invoice Line
        self.invoice_line = self.account_invoice_line.create(
            {'name': 'Test invoice line',
             'account_id': self.invoice_account.id,
             'quantity': 1.000,
             'price_unit': 2.99})

        self.current_user.company_id.invoice_date_required = True

    def test_account_invoice_date_required(self):
        invoice = self.account_invoice.create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'account_id': self.invoice_account.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(6, 0, [self.invoice_line.id])]
        })
        self.assertEquals(
            1,
            len(invoice),
        )
        with self.assertRaises(ValidationError):
            self.account_invoice.create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'account_id': self.invoice_account.id,
                'type': 'out_invoice',
                'invoice_line_ids': [(6, 0, [self.invoice_line.id])]
            }).action_invoice_open()

    def test_account_invoice_date_not_required(self):
        self.current_user.company_id.invoice_date_required = False
        self.account_invoice.create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'account_id': self.invoice_account.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(6, 0, [self.invoice_line.id])]
        }).action_invoice_open()
