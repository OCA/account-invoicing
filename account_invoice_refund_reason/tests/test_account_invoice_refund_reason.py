# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase
import datetime


class TestAccountInvoiceRefundReason(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceRefundReason, self).setUp()

        self.account_invoice_obj = self.env['account.invoice']
        self.account_obj = self.env['account.account']
        self.journal_obj = self.env['account.journal']
        self.invoice_refund_obj = self.env['account.invoice.refund']
        self.reason_obj = self.env['account.invoice.refund.reason']

        self.payment_term = \
            self.env.ref('account.account_payment_term_advance')
        self.partner3 = self.env.ref('base.res_partner_3')
        self.account_user_type =\
            self.env.ref('account.data_account_type_receivable')
        self.product_id = self.env.ref('product.product_product_5')
        self.account_revenue = \
            self.env.ref('account.data_account_type_revenue')

        self.journalrec = self.journal_obj.search([('type', '=', 'sale')])[0]
        self.account_id = self.account_obj.search([
            ('user_type_id', '=', self.account_revenue.id)], limit=1)
        self.reason_id = self.env.ref('account_invoice_refund_reason.'
                                      'refund_reason_cancellation')

        self.account_rec1_id = self.account_obj.create(dict(
            code="cust_acc",
            name="customer account",
            user_type_id=self.account_user_type.id,
            reconcile=True,
        ))
        invoice_line_data = [
            (0, 0,
                {
                    'product_id': self.product_id.id,
                    'quantity': 10.0,
                    'account_id': self.account_id.id,
                    'name': 'product test 5',
                    'price_unit': 100.00,
                }
             )
        ]

        self.account_invoice_customer0 = self.account_invoice_obj.create(dict(
            name="Test Customer Invoice",
            payment_term_id=self.payment_term.id,
            journal_id=self.journalrec.id,
            partner_id=self.partner3.id,
            account_id=self.account_rec1_id.id,
            invoice_line_ids=invoice_line_data
        ))

    def test_onchange_reason_id(self):
        self.account_invoice_customer0.action_invoice_open()

        self.account_invoice_refund_0 = self.invoice_refund_obj.create(dict(
            description='Credit Note',
            date=datetime.date.today(),
            filter_refund='refund',
            reason_id=self.reason_id.id
        ))

        self.account_invoice_refund_0._onchange_reason_id()
        self.assertEqual(self.account_invoice_refund_0.description,
                         self.account_invoice_refund_0.reason_id.name)
        self.account_invoice_refund_0.invoice_refund()
        self.assertEqual(self.account_invoice_customer0.reason_id.id,
                         self.reason_id.id)
