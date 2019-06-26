# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestAccountBilling(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal_sale = cls.env['account.journal'].search([
            ('type', '=', 'sale')])[0]
        cls.invoice_model = cls.env['account.invoice']
        cls.invoice_line_model = cls.env['account.invoice.line']
        cls.billing_model = cls.env['account.billing']
        cls.register_payments_model = cls.env['account.register.payments']

        cls.partner_agrolait = cls.env.ref("base.res_partner_2")
        cls.partner_china_exp = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_product_4")
        cls.currency_chf_id = cls.env.ref("base.CHF").id
        cls.currency_usd_id = cls.env.ref("base.USD").id
        cls.currency_eur_id = cls.env.ref("base.EUR").id

        cls.account_receivable = cls.env['account.account'].search([
            ('user_type_id', '=',
             cls.env.ref('account.data_account_type_receivable').id)], limit=1)
        cls.account_revenue = cls.env['account.account'].search([
            ('user_type_id', '=',
             cls.env.ref('account.data_account_type_revenue').id)], limit=1)
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in")
        cls.journal_bank = cls.env['account.journal'].create(
            {'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})

        cls.inv_1 = cls.create_invoice(
            cls, amount=100, currency_id=cls.currency_eur_id,
            partner=cls.partner_agrolait.id)
        cls.inv_2 = cls.create_invoice(
            cls, amount=200, currency_id=cls.currency_eur_id,
            partner=cls.partner_agrolait.id)
        cls.inv_3 = cls.create_invoice(
            cls, amount=300, currency_id=cls.currency_usd_id,
            partner=cls.partner_agrolait.id)
        cls.inv_4 = cls.create_invoice(
            cls, amount=400, currency_id=cls.currency_eur_id,
            partner=cls.partner_china_exp.id)

    def create_invoice(self, amount=None, type='out_invoice',
                       currency_id=None, partner=None, account_id=None):
        """ Returns an open invoice """
        invoice = self.invoice_model.create({
            'partner_id': partner or self.partner_agrolait.id,
            'currency_id': currency_id or self.currency_eur_id,
            'name': type,
            'account_id': account_id or self.account_receivable.id,
            'type': type
        })
        self.invoice_line_model.create({
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': amount,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': self.account_revenue.id,
        })
        invoice.action_invoice_open()
        return invoice

    def create_payment(self, ctx):
        register_payments = \
            self.register_payments_model.with_context(ctx).create({
                'journal_id': self.journal_bank.id,
                'payment_method_id': self.payment_method_manual_in.id
            })
        return register_payments.create_payments()

    def test_1_invoice_partner(self):
        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.inv_1.id, self.inv_4.id],
               'bill_type': 'out_invoice'}
        with self.assertRaises(ValidationError):
            self.billing_model.with_context(ctx).create({})

    def test_2_invoice_currency(self):
        ctx1 = {'active_model': 'account.invoice',
                'active_ids': [self.inv_1.id, self.inv_3.id],
                'bill_type': 'out_invoice'}
        with self.assertRaises(ValidationError):
            self.billing_model.with_context(ctx1).create({})
        # create billing directly
        self.billing_model.create({'partner_id': self.partner_agrolait.id})

    def test_3_validate_billing_state_not_open(self):
        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.inv_1.id]}
        self.create_payment(ctx)
        customer_billing = self.billing_model.with_context(ctx).create({})
        with self.assertRaises(ValidationError):
            customer_billing.validate_billing()

    def test_4_billing_fields_view_get(self):
        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.inv_1.id]}
        customer_billing = self.billing_model.with_context(ctx).create({})
        # check invoice is billed
        with self.assertRaises(ValidationError):
            customer_billing.fields_view_get()

        self.create_payment(ctx)
        # check invoice is state paid
        customer_billing = self.billing_model.with_context(ctx).create({})
        with self.assertRaises(ValidationError):
            customer_billing.fields_view_get()

    def test_5_create_billing_from_selected_invoices(self):
        """ Create two invoices, post it and send context to Billing """
        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.inv_1.id, self.inv_2.id],
               'bill_type': 'out_invoice'}
        customer_billing1 = self.billing_model.with_context(ctx).create({})
        self.assertEqual(customer_billing1.state, 'draft')
        customer_billing1.validate_billing()
        self.assertEqual(customer_billing1.state, 'billed')
        self.assertEqual(customer_billing1.invoice_related_count, 2)
        customer_billing1.invoice_relate_billing_tree_view()
        customer_billing1.action_cancel()
        customer_billing1.action_cancel_draft()

        customer_billing2 = self.billing_model.with_context(ctx).create({})
        customer_billing2.validate_billing()
        self.create_payment(ctx)
        with self.assertRaises(ValidationError):
            customer_billing2.action_cancel()
