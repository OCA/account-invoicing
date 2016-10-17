# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp import workflow


class TestAccountInvoiceBlocking(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceBlocking, self).setUp()

        # ENVIRONEMENTS

        self.account_invoice = self.env['account.invoice']
        self.account_move_line = self.env['account.move.line']
        self.account_account = self.env['account.account']
        self.account_journal = self.env['account.journal']
        self.account_invoice_line = self.env['account.invoice.line']

        # INSTANCES

        # Instance: company
        self.company = self.env.ref('base.main_company')

        # Instance: account type (receivable)
        self.type_recv = self.env.ref('account.data_account_type_receivable')

        # Instance: account type (payable)
        self.type_payable = self.env.ref('account.data_account_type_payable')

        # Instance: account (receivable)
        self.account_recv = self.account_account.create({
            'name': 'test_account_receivable',
            'code': '123',
            'user_type_id': self.type_recv.id,
            'company_id': self.company.id,
            'reconcile': True})

        # Instance: account (payable)
        self.account_payable = self.account_account.create({
            'name': 'test_account_payable',
            'code': '321',
            'user_type_id': self.type_payable.id,
            'company_id': self.company.id,
            'reconcile': True})

        # Instance: partner
        self.partner = self.env.ref('base.res_partner_2')

        # Instance: journal
        self.journal = self.account_journal.search([('code', '=', 'BILL')])

        # Instance: product
        self.product = self.env.ref('product.product_product_4')

        # Instance: invoice line
        self.invoice_line = self.account_invoice_line.create({
            'name': 'test',
            'account_id': self.account_payable.id,
            'price_unit': 2000.00,
            'quantity': 1,
            'product_id': self.product.id})

        # Instance: invoice
        self.invoice = self.account_invoice.create({
            'partner_id': self.partner.id,
            'account_id': self.account_recv.id,
            'payment_term': False,
            'journal_id': self.journal.id,
            'invoice_line_ids': [(4, self.invoice_line.id)]})

    def test_invoice(self):
        self.account_invoice.search([('id', '=', self.invoice.id)])
        self.invoice.draft_blocked = True

        workflow.trg_validate(self.uid, 'account.invoice', self.invoice.id,
                              'invoice_open', self.cr)
        move_line = self.account_move_line.search(
            [('account_id.user_type_id', 'in', [self.type_recv.id,
                                                self.type_payable.id]),
             ('invoice_id', '=', self.invoice.id)])
        if move_line:
            self.assertTrue(move_line[0].blocked)
            self.assertEqual(self.invoice.blocked, move_line[0].blocked,
                             'Blocked values are not equals')
            move_line[0].blocked = False
            self.invoice = self.account_invoice.search([('id',
                                                         '=',
                                                         self.invoice.id)])
            self.assertEqual(self.invoice.blocked, move_line[0].blocked,
                             'Blocked values are not equals')
            self.invoice.blocked = True
            self.invoice = self.account_invoice.search([('id',
                                                         '=',
                                                         self.invoice.id)])
            self.assertEqual(self.invoice.blocked, move_line[0].blocked,
                             'Blocked values are not equals')
