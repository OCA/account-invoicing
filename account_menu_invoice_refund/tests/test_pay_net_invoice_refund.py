# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import UserError


class TestAccountMenuInvoiceRefund(TransactionCase):

    def test_pay_net_invoice_refund(self):
        """By selecting 1 invoice and 1 refund document,
        I expect to net pay all document in one go."""
        invoice_line1_vals = [
            (0, 0, {
                'product_id': self.env.ref('product.product_product_2').id,
                'quantity': 1.0,
                'account_id': self.env['account.account'].search(
                    [('user_type_id', '=', self.env.ref(
                        'account.data_account_type_revenue').id)],
                    limit=1).id,
                'name': 'Product A',
                'price_unit': 450.00
                })
        ]
        invoice_line2_vals = [
            (0, 0, {
                'product_id': self.env.ref('product.product_product_3').id,
                'quantity': 1.0,
                'account_id': self.env['account.account'].search(
                    [('user_type_id', '=', self.env.ref(
                        'account.data_account_type_revenue').id)],
                    limit=1).id,
                'name': 'Product B',
                'price_unit': 200.00
                })
        ]
        # 2 products = 650
        invoice = self.env['account.invoice'].create({
            'name': 'Test Customer Invoice',
            'type': 'out_invoice',
            'journal_id': self.env['account.journal'].search(
                [('type', '=', 'sale')], limit=1).id,
            'partner_id': self.env.ref('base.res_partner_12').id,
            'account_id': self.env['account.account'].search(
                [('user_type_id', '=', self.env.ref(
                    'account.data_account_type_receivable').id)],
                limit=1).id,
            'invoice_line_ids': invoice_line1_vals + invoice_line2_vals,
        })
        # refund 1 product = 200
        refund = self.env['account.invoice'].create({
            'name': "Test Customer Refund",
            'type': 'out_refund',
            'journal_id': self.env['account.journal'].search(
                [('type', '=', 'sale')], limit=1).id,
            'partner_id': self.env.ref('base.res_partner_12').id,
            'account_id': self.env['account.account'].search(
                [('user_type_id', '=', self.env.ref(
                    'account.data_account_type_receivable').id)],
                limit=1).id,
            'invoice_line_ids': invoice_line2_vals,
        })
        invoice.action_invoice_open()
        ctx = {'active_ids': [invoice.id, refund.id],
               'active_model': 'account.invoice'}
        # Make payment with net amount = 450, both invoice/refund is paid
        PaymentWizard = self.env['account.register.payments']
        view_id = ('account.view_account_payment_from_invoices')

        # Test exception case, when refund currency is different
        wrong_currency = self.env['res.currency'].search([
            ('id', '!=', invoice.currency_id.id)], limit=1)
        wrong_refund = refund.copy({'currency_id': wrong_currency.id})
        wrong_refund.action_invoice_open()
        ctx = {'active_ids': [invoice.id, wrong_refund.id],
               'active_model': 'account.invoice'}
        with self.assertRaises(UserError):  # Test wrong currency
            Form(PaymentWizard.with_context(ctx), view=view_id)

        # Switch back to the valid refund, and try to make payment
        ctx = {'active_ids': [invoice.id, refund.id],
               'active_model': 'account.invoice'}
        with self.assertRaises(UserError):  # Test doc status exception
            Form(PaymentWizard.with_context(ctx), view=view_id)
        refund.action_invoice_open()
        # Finally, do the payment
        f = Form(PaymentWizard.with_context(ctx), view=view_id)
        payment = f.save()
        payment.create_payments()
        self.assertEqual(invoice.state, 'paid')
        self.assertEqual(refund.state, 'paid')
