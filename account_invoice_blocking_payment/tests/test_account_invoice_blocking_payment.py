# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.exceptions import UserError
from openerp.tests.common import SavepointCase


class TestAccountInvoiceBlockingPayment(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceBlockingPayment, cls).setUpClass()

        # ENVIRONMENTS

        cls.account_account = cls.env['account.account']
        cls.account_invoice = cls.env['account.invoice']
        cls.account_invoice_line = cls.env['account.invoice.line']
        cls.account_journal = cls.env['account.journal']
        cls.account_move_line = cls.env['account.move.line']
        cls.account_payment_line = cls.env['account.payment.line']
        cls.account_payment_method = cls.env['account.payment.method']
        cls.account_payment_mode = cls.env['account.payment.mode']
        cls.account_payment_order = cls.env['account.payment.order']

        # INSTANCES

        # Payment method
        cls.payment_method = cls.account_payment_method.create({
            'name': 'Test payment method',
            'code': 'TPM',
            'payment_type': 'outbound',
            'bank_account_required': False,
            'active': True
        })

        # Account (440000 Entreprises liées)
        cls.account_440000 = cls.account_account.create({
            'name': 'Entreprises liées',
            'code': '440000_demo',
            'user_type_id':
                cls.env.ref('account.data_account_type_payable').id,
            'reconcile': True})
        # Account (600000 Achats de matières premières)
        cls.account_600000 = cls.account_account.create({
            'name': 'Achats matières premières',
            'code': '600000_demo',
            'user_type_id':
                cls.env.ref('account.data_account_type_expenses').id,
            'reconcile': False})
        # Account (451055 T.V.A. à payer - Intra-communautaire)
        cls.account_451055 = cls.account_account.create({
            'name': 'T.V.A. à payer - Intra-communautaire',
            'code': '451055_demo',
            'user_type_id':
                cls.env.ref('account'
                            '.data_account_type_current_liabilities').id,
            'reconcile': True,
            'vat_due': True})
        # Account expenses
        cls.account_exp = cls.account_account.create({
            'code': 'X2120',
            'name': 'Expenses - (test)',
            'user_type_id':
                cls.env.ref('account.data_account_type_expenses').id
        })

        # Journal
        cls.journal = cls.account_journal.create({
            'name': 'Test journal vendor bills',
            'code': 'TJVB',
            'type': 'purchase',
            'default_debit_account_id': cls.account_exp.id,
            'default_credit_account_id': cls.account_exp.id,
            'refund_sequence': True
        })

        # Payment mode
        cls.payment_mode = cls.account_payment_mode.create({
            'name': 'Test payment mode',
            'payment_method_id': cls.payment_method.id,
            'payment_type': 'outbound',
            'payment_order_id': True,
            'bank_account_link': 'fixed',
            'fixed_journal_id': cls.journal.id
        })

        # Invoice lines
        cls.invoice_line_1 = cls.account_invoice_line.create({
            'name': 'Invoice line 1',
            'quantity': 2,
            'price_unit': 2.5,
            'account_id': cls.account_600000.id})

        # Partner
        cls.partner = cls.env.ref('base.res_partner_2')

        # Invoice
        cls.invoice = cls.account_invoice.create({
            'type': 'in_invoice',
            'partner_id': cls.partner.id,
            'account_id': cls.account_440000.id,
            'journal_id': cls.journal.id,
            'payment_mode_id': cls.payment_mode.id,
            'reference': '123456',
            'invoice_line_ids':
                [(6, 0, [cls.invoice_line_1.id])]})

    def test_create_account_payment_line_blocked(self):
        """
        Test: payment button on blocked invoice
        """
        with self.assertRaises(UserError):
            self.invoice.draft_blocked = True
            self.invoice.blocked = True
            self.invoice.action_move_create()
            self.invoice.state = 'open'
            self.invoice.create_account_payment_line()

    def test_create_account_payment_line_not_blocked(self):
        """
        Test: payment button on not blocked invoice
        """
        self.invoice.action_move_create()
        self.invoice.state = 'open'
        self.invoice.create_account_payment_line()
        nb_pl = self.account_payment_line.search_count([
            ('move_line_id', 'in', self.invoice.move_id.line_ids.ids)])
        self.assertEqual(nb_pl, 1)
