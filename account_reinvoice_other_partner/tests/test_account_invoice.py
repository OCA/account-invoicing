# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields


class TestAccountInvoice(TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        # ENVIRONMENTS
        self.account_invoice = self.env['account.invoice']
        self.account_model = self.env['account.account']
        self.account_invoice_line = self.env['account.invoice.line']
        self.current_user = self.env.user
        self.register_payments = self.env['account.register.payments']
        self.payment = self.env['account.payment']

        # INSTANCES
        self.main_company = self.env.ref('base.main_company')
        self.other_currency = self.env['res.currency'].create(
            {'name': 'other currency',
             'symbol': 'other'})
        self.env['res.currency.rate'].create({
            'name': fields.Date.today(),
            'rate': 2.0,
            'currency_id': self.other_currency.id,
            'company_id': self.main_company.id
        })
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in")
        self.receivable_act = self.env.ref(
            'account.data_account_type_receivable')
        # Instance: Account
        self.revenue_act = self.env.ref('account.data_account_type_revenue')
        self.journalrec = self.env['account.journal'].search(
            [('type', '=', 'sale')])[0]
        self.journalbank = self.env['account.journal'].search(
            [('type', '=', 'bank')])[0]
        self.journalgeneral = self.env['account.journal'].search(
            [('type', '=', 'general')])[0]
        self.receivable_acc = self.account_model.search([
            ('user_type_id',
             '=', self.receivable_act.id)], limit=1)
        self.revenue_acc = self.account_model.search([
            ('user_type_id',
             '=', self.revenue_act.id)], limit=1)
        self.partner_1 = self.env['res.partner'].create({
            'name': 'Customer person',
            'property_account_receivable_id': self.receivable_acc.id,
        })
        self.partner_2 = self.env['res.partner'].create({
            'name': 'Customer Company',
            'property_account_receivable_id': self.receivable_acc.id,
        })
        self.main_company.reinvoice_journal_id = self.journalgeneral

    def test_reinvoice_other_partner_multi(self):
        """Test generating multiple new invoices"""
        invoice_1 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_1.action_invoice_open()

        invoice_2 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 2000.00}
                                  )]
        })
        invoice_2.action_invoice_open()

        invoice_3 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'type': 'out_refund',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_3.action_invoice_open()
        # Create a payment
        ctx = {'active_model': 'account.invoice',
               'active_ids': [invoice_1.id]
               }
        register_payments = self.register_payments.with_context(ctx).create({
            'payment_date': fields.Date.today(),
            'journal_id': self.journalbank.id,
            'payment_method_id': self.payment_method_manual_in.id,
        })
        register_payments.amount = 100
        register_payments.create_payments()

        invoices = invoice_1.ids + invoice_2.ids + invoice_3.ids
        # Create credit and change partner
        context = {"active_model": 'account.invoice',
                   "active_ids": invoices,
                   }
        wiz = self.env['account.reinvoice.other.partner'].with_context(
            context).create({
                'new_partner_id': self.partner_2.id,
            })
        wiz.process()
        self.assertEquals(invoice_1.state, 'paid')
        self.assertEquals(invoice_2.state, 'paid')
        invs = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEquals(len(invs), 3)
        partner_1_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_1.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p1 = sum(partner_1_receivables.mapped('amount_residual'))
        self.assertEquals(residual_p1, 0.0)

        partner_2_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_2.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p2 = sum(partner_2_receivables.mapped('amount_residual'))
        self.assertEquals(residual_p2, 1900.00)

    def test_reinvoice_other_partner_single(self):
        """Test generating a single new invoice"""
        invoice_1 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_1.action_invoice_open()

        invoice_2 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 2000.00}
                                  )]
        })
        invoice_2.action_invoice_open()

        invoice_3 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'type': 'out_refund',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_3.action_invoice_open()
        # Create a payment
        ctx = {'active_model': 'account.invoice',
               'active_ids': [invoice_1.id]
               }
        register_payments = self.register_payments.with_context(ctx).create({
            'payment_date': fields.Date.today(),
            'journal_id': self.journalbank.id,
            'payment_method_id': self.payment_method_manual_in.id,
        })
        register_payments.amount = 100
        register_payments.create_payments()

        invoices = invoice_1.ids + invoice_2.ids + invoice_3.ids
        # Create credit and change partner
        context = {"active_model": 'account.invoice',
                   "active_ids": invoices,
                   }
        wiz = self.env['account.reinvoice.other.partner'].with_context(
            context).create({
                'new_partner_id': self.partner_2.id,
                'single_invoice': True,
            })
        wiz.process()
        self.assertEquals(invoice_1.state, 'paid')
        self.assertEquals(invoice_2.state, 'paid')
        invs = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEquals(len(invs), 1)
        self.assertEquals(invs[0].type, 'out_invoice')
        partner_1_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_1.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p1 = sum(partner_1_receivables.mapped('amount_residual'))
        self.assertEquals(residual_p1, 0.0)

        partner_2_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_2.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p2 = sum(partner_2_receivables.mapped('amount_residual'))
        self.assertEquals(residual_p2, 1900.00)

    def test_reinvoice_other_partner_currency_multi(self):
        """Test generating multiple new invoices using another currency"""
        invoice_1 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'currency_id': self.other_currency.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_1.action_invoice_open()

        invoice_2 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'currency_id': self.other_currency.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 2000.00}
                                  )]
        })
        invoice_2.action_invoice_open()

        invoice_3 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'currency_id': self.other_currency.id,
            'type': 'out_refund',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_3.action_invoice_open()
        # Create a payment
        ctx = {'active_model': 'account.invoice',
               'active_ids': [invoice_1.id]
               }
        register_payments = self.register_payments.with_context(ctx).create({
            'payment_date': fields.Date.today(),
            'journal_id': self.journalbank.id,
            'payment_method_id': self.payment_method_manual_in.id,
        })
        register_payments.amount = 100
        register_payments.create_payments()

        invoices = invoice_1.ids + invoice_2.ids + invoice_3.ids
        # Create credit and change partner
        context = {"active_model": 'account.invoice',
                   "active_ids": invoices,
                   }
        wiz = self.env['account.reinvoice.other.partner'].with_context(
            context).create({
                'new_partner_id': self.partner_2.id,
            })
        wiz.process()
        self.assertEquals(invoice_1.state, 'paid')
        self.assertEquals(invoice_2.state, 'paid')
        invs = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEquals(len(invs), 3)
        partner_1_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_1.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p1 = sum(partner_1_receivables.mapped(
            'amount_residual_currency'))
        self.assertEquals(residual_p1, 0.0)

        partner_2_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_2.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p2 = sum(partner_2_receivables.mapped(
            'amount_residual_currency'))
        self.assertEquals(residual_p2, 1900.00)

    def test_reinvoice_other_partner_currency_single(self):
        """Test generating a single new invoice using a different currency"""
        invoice_1 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'currency_id': self.other_currency.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_1.action_invoice_open()

        invoice_2 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'currency_id': self.other_currency.id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 2000.00}
                                  )]
        })
        invoice_2.action_invoice_open()

        invoice_3 = self.account_invoice.create({
            'partner_id': self.partner_1.id,
            'company_id': self.main_company.id,
            'account_id': self.receivable_acc.id,
            'currency_id': self.other_currency.id,
            'type': 'out_refund',
            'invoice_line_ids': [(0, 0,
                                  {'name': 'Test invoice line',
                                   'account_id': self.revenue_acc.id,
                                   'quantity': 1.000,
                                   'price_unit': 1000.00}
                                  )]
        })
        invoice_3.action_invoice_open()
        # Create a payment
        ctx = {'active_model': 'account.invoice',
               'active_ids': [invoice_1.id]
               }
        register_payments = self.register_payments.with_context(ctx).create({
            'payment_date': fields.Date.today(),
            'journal_id': self.journalbank.id,
            'payment_method_id': self.payment_method_manual_in.id,
        })
        register_payments.amount = 100
        register_payments.create_payments()

        invoices = invoice_1.ids + invoice_2.ids + invoice_3.ids
        # Create credit and change partner
        context = {"active_model": 'account.invoice',
                   "active_ids": invoices,
                   }
        wiz = self.env['account.reinvoice.other.partner'].with_context(
            context).create({
                'new_partner_id': self.partner_2.id,
                'single_invoice': True,
            })
        wiz.process()
        self.assertEquals(invoice_1.state, 'paid')
        self.assertEquals(invoice_2.state, 'paid')
        invs = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEquals(len(invs), 1)
        self.assertEquals(invs[0].type, 'out_invoice')
        partner_1_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_1.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p1 = sum(partner_1_receivables.mapped(
            'amount_residual_currency'))
        self.assertEquals(residual_p1, 0.0)

        partner_2_receivables = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_2.id),
             ('account_id', '=', self.receivable_acc.id)])
        residual_p2 = sum(partner_2_receivables.mapped(
            'amount_residual_currency'))
        self.assertEquals(residual_p2, 1900.00)
