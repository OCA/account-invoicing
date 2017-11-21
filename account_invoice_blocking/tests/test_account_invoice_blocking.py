# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceBlocking(TransactionCase):

    def setUp(self):
        """
        Setup test instances
        """
        super(TestAccountInvoiceBlocking, self).setUp()

        company = self.env.ref('base.main_company')

        # Instance: account type (receivable)
        self.type_recv = self.env.ref('account.data_account_type_receivable')

        # Instance: account type (payable)
        self.type_payable = self.env.ref('account.data_account_type_payable')

        # account (receivable)
        account_recv = self.env['account.account'].create({
            'name': 'test_account_receivable',
            'code': '123',
            'user_type_id': self.type_recv.id,
            'company_id': company.id,
            'reconcile': True})

        # account (payable)
        account_payable = self.env['account.account'].create({
            'name': 'test_account_payable',
            'code': '321',
            'user_type_id': self.type_payable.id,
            'company_id': company.id,
            'reconcile': True})

        partner = self.env.ref('base.res_partner_2')
        journal = self.env['account.journal'].search([('code', '=', 'BILL')])
        product = self.env.ref('product.product_product_4')

        invoice_line = self.env['account.invoice.line'].create({
            'name': 'test',
            'account_id': account_payable.id,
            'price_unit': 2000.00,
            'quantity': 1,
            'product_id': product.id})

        # Instance: invoice
        self.invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'account_id': account_recv.id,
            'payment_term_id': False,
            'journal_id': journal.id,
            'invoice_line_ids': [(4, invoice_line.id)]})

    def test_01_invoice_blocking(self):
        """
        Test Blocking Invoice
        """

        self.invoice.draft_blocked = True
        self.invoice.action_invoice_open()

        types_list = [self.type_recv.id, self.type_payable.id]
        move_lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', 'in', types_list),
            ('invoice_id', '=', self.invoice.id)
        ])
        self.assertTrue(move_lines)
        for move_line in move_lines:
            self.assertTrue(move_line.blocked)
            self.assertEqual(
                self.invoice.blocked, move_line.blocked,
                'Blocked values are not equals')

        self.invoice = self.env['account.invoice'].search([
            ('id', '=', self.invoice.id)
        ])
        for move_line in move_lines:
            move_line.blocked = False
            self.assertEqual(
                self.invoice.blocked, move_line.blocked,
                'Blocked values are not equals')

        self.invoice = self.env['account.invoice'].search([
            ('id', '=', self.invoice.id)
        ])
        self.invoice.blocked = True
        for move_line in move_lines:
            self.assertEqual(
                self.invoice.blocked, move_line.blocked,
                'Blocked values are not equals')
