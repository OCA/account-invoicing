# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields


class TestAccountInvoiceAlternateCommercialPartner(TransactionCase):

    def setUp(self):
        """
        Setup test instances
        """
        super(TestAccountInvoiceAlternateCommercialPartner, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.currency_usd_id = self.env.ref("base.USD").id
        # Instance: account type (receivable)
        self.type_recv = self.env.ref('account.data_account_type_receivable')
        # Instance: account type (payable)
        self.type_payable = self.env.ref('account.data_account_type_payable')
        # Instance: account type (expense)
        self.type_expense = self.env.ref('account.data_account_type_expenses')
        # Instance: account type (revenue)
        self.type_revenue = self.env.ref('account.data_account_type_revenue')
        self.register_payments_model = self.env['account.register.payments']
        # account (receivable)
        self.account_recv = self.env['account.account'].create({
            'name': 'test_account_receivable',
            'code': '123',
            'user_type_id': self.type_recv.id,
            'company_id': self.company.id,
            'reconcile': True})
        # account (payable)
        self.account_payable = self.env['account.account'].create({
            'name': 'test_account_payable',
            'code': '321',
            'user_type_id': self.type_payable.id,
            'company_id': self.company.id,
            'reconcile': True})
        self.account_payable_2 = self.env['account.account'].create({
            'name': 'test_account_payable',
            'code': '3211',
            'user_type_id': self.type_payable.id,
            'company_id': self.company.id,
            'reconcile': True})
        self.account_expense = self.env['account.account'].create({
            'name': 'test_account_expense',
            'code': 'expense',
            'user_type_id': self.type_expense.id,
            'company_id': self.company.id,
            'reconcile': False})
        self.account_revenue = self.env['account.account'].create({
            'name': 'test_account_revenue',
            'code': 'revenue',
            'user_type_id': self.type_revenue.id,
            'company_id': self.company.id,
            'reconcile': False})
        self.customer_commercial = self.env['res.partner'].create({
            'name': 'Customer commercial partner',
            'property_account_receivable_id': self.account_recv.id,
            'is_company': True,
        })
        self.customer = self.env['res.partner'].create({
            'name': 'Customer',
            'property_account_receivable_id': self.account_recv.id,
            'company_id': self.company.id,
            'parent_id': self.customer_commercial.id,
        })
        self.vendor_commercial = self.env['res.partner'].create({
            'name': 'Vendor commercial partner',
            'property_account_payable_id': self.account_payable.id,
            'is_company': True,
        })
        self.vendor = self.env['res.partner'].create({
            'name': 'Vendor',
            'property_account_payable_id': self.account_payable.id,
            'company_id': self.company.id,
            'parent_id': self.vendor_commercial.id,
        })
        self.payor = self.env['res.partner'].create({
            'name': 'Payor for customer',
            'property_account_receivable_id': self.account_recv.id,
            'company_id': self.company.id,
        })
        self.payee = self.env['res.partner'].create({
            'name': 'Payee for vendor',
            'property_account_payable_id': self.account_payable_2.id,
            'company_id': self.company.id,
        })
        self.payee_bank = self.env['res.partner.bank'].create({
            'partner_id': self.payee.id,
            'acc_number': 'ES66 2100 0418 4012 3456 7891',
            'company_id': self.company.id,
        })
        self.purchase_journal = self.env['account.journal'].create(
            {'name': 'Purchase Journal - TST',
             'code': 'PJT',
             'type': 'purchase',
             'company_id': self.company.id})
        self.sale_journal = self.env['account.journal'].create(
            {'name': 'Sale Journal - TST',
             'code': 'SJT',
             'type': 'sale',
             'company_id': self.company.id})
        self.bank_journal_usd = self.env['account.journal'].create(
            {'name': 'Bank US TEST', 'type': 'bank', 'code': 'BJT'})
        self.product = self.env['product.product'].create({
            'type': 'service',
            'name': 'Sample product'
        })
        self.invoice_line = self.env['account.invoice.line'].create({
            'name': 'test',
            'account_id': self.account_expense.id,
            'price_unit': 2000.00,
            'quantity': 1,
            'product_id': self.product.id})
        # Instance: invoice
        self.vendor_invoice = self.env['account.invoice'].create({
            'partner_id': self.vendor.id,
            'type': 'in_invoice',
            'account_id': self.account_payable.id,
            'payment_term_id': False,
            'journal_id': self.purchase_journal.id,
            'company_id': self.company.id,
            'currency_id': self.currency_usd_id,
            'invoice_line_ids': [(4, self.invoice_line.id)]})
        invoice_line = self.env['account.invoice.line'].create({
            'name': 'test',
            'account_id': self.account_revenue.id,
            'price_unit': 2000.00,
            'quantity': 1,
            'product_id': self.product.id})
        # Instance: invoice
        self.customer_invoice = self.env['account.invoice'].create({
            'partner_id': self.customer.id,
            'type': 'out_invoice',
            'account_id': self.account_recv.id,
            'payment_term_id': False,
            'journal_id': self.sale_journal.id,
            'company_id': self.company.id,
            'currency_id': self.currency_usd_id,
            'invoice_line_ids': [(4, invoice_line.id)]})

    def test_01_onchange(self):
        # Instance: invoice
        supplier_invoice = self.env['account.invoice'].new({
            'partner_id': self.vendor.id,
            'type': 'in_invoice',
            'account_id': self.account_payable.id,
            'payment_term_id': False,
            'journal_id': self.purchase_journal.id,
            'currency_id': self.currency_usd_id,
            'company_id': self.company.id,
            'invoice_line_ids': [
                (0, 0, {'name': 'test',
                        'account_id': self.account_expense.id,
                        'price_unit': 2000.00,
                        'quantity': 1,
                        'product_id': self.product.id
                        }
                 )
            ]})
        supplier_invoice.alternate_payer_id = self.payee
        supplier_invoice._onchange_partner_id()
        self.assertEqual(supplier_invoice.partner_bank_id, self.payee_bank)
        self.assertEqual(supplier_invoice.account_id, self.account_payable_2)

    def test_02_invoice(self):
        """
        Test Setting an alternate commercial partner
        """
        # Customer invoices
        self.customer_invoice.alternate_payer_id = self.payor.id
        self.customer_invoice._onchange_partner_id()
        self.customer_invoice.action_invoice_open()
        self.assertEqual(self.customer_invoice.state, 'open')
        line = self.customer_invoice.move_id.line_ids.filtered(
            lambda li: li.account_id == self.account_recv)
        self.assertEqual(line.partner_id, self.payor)
        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.customer_invoice.id]}
        register_payments = self.register_payments_model.with_context(
            ctx).create({
                'payment_date': fields.Date.today(),
                'journal_id': self.bank_journal_usd.id,
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_in').id,
                })
        register_payments.create_payments()
        self.assertEqual(self.customer_invoice.state, 'paid')
        # Vendor bills
        self.vendor_invoice.alternate_payer_id = self.payee
        self.vendor_invoice._onchange_partner_id()
        self.vendor_invoice.action_invoice_open()
        self.assertEqual(self.vendor_invoice.state, 'open')
        line = self.vendor_invoice.move_id.line_ids.filtered(
            lambda li: li.account_id == self.account_payable_2)
        self.assertEqual(line.partner_id, self.payee)
        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.vendor_invoice.id]
               }
        register_payments = self.register_payments_model.with_context(
            ctx).create({
                'payment_date': fields.Date.today(),
                'journal_id': self.bank_journal_usd.id,
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_out').id,
                })
        register_payments.create_payments()
        self.assertEqual(self.vendor_invoice.state, 'paid')

    def test_03_payment_multiple_invoices(self):
        """
            Test selecting multiple invoices with different alternate payer
        """
        supplier_invoice_1 = self.env['account.invoice'].create({
            'partner_id': self.customer.id,
            'type': 'in_invoice',
            'account_id': self.account_payable.id,
            'payment_term_id': False,
            'journal_id': self.purchase_journal.id,
            'currency_id': self.currency_usd_id,
            'company_id': self.company.id,
            'invoice_line_ids': [
                (0, 0, {'name': 'test',
                        'account_id': self.account_expense.id,
                        'price_unit': 2000.00,
                        'quantity': 1,
                        'product_id': self.product.id
                        }
                 )
            ]})
        supplier_invoice_2 = supplier_invoice_1.copy()
        supplier_invoice_2.alternate_payer_id = self.payee
        supplier_invoice_3 = supplier_invoice_1.copy()
        supplier_invoice_1._onchange_partner_id()
        supplier_invoice_1.action_invoice_open()
        supplier_invoice_2._onchange_partner_id()
        supplier_invoice_2.action_invoice_open()
        supplier_invoice_3._onchange_partner_id()
        supplier_invoice_3.action_invoice_open()
        ctx = {'active_model': 'account.invoice',
               'active_ids': [supplier_invoice_1.id, supplier_invoice_2.id,
                              supplier_invoice_3.id]}
        register_payments = self.register_payments_model.with_context(
            ctx).create({
                'payment_date': fields.Date.today(),
                'journal_id': self.bank_journal_usd.id,
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_out').id,
                })
        res = register_payments.create_payments()
        # ['domain'][('id', 'in', payments.ids), ('state', '=', 'posted')]
        self.assertEqual(len(res['domain'][0][2]), 2)
        self.assertEqual(supplier_invoice_1.state, 'paid')
        self.assertEqual(supplier_invoice_2.state, 'paid')
        self.assertEqual(supplier_invoice_3.state, 'paid')
