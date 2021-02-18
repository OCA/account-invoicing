import odoo.tests.common as common
from odoo import fields, exceptions


class TestAccountPaymentTermDateRanges(common.TransactionCase):

    def setUp(self):
        super(TestAccountPaymentTermDateRanges, self).setUp()
        self.invoice_model = self.env['account.invoice']
        journal_model = self.env['account.journal']
        self.journal = journal_model.search([('type', '=', 'purchase')])
        self.partner = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_5')
        self.prod_account = self.env.ref('account.demo_coffee_machine_account')
        self.inv_account = self.env.ref('account.demo_sale_of_land_account')
        self.payment_term = self.env.ref(
            "account_payment_term_date_range.account_payment_term_date_ranges")

    def test_invoice_normal_payment_term(self):

        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term.id,
             'date_invoice': '%s-01-01' % fields.datetime.now().year,
             'type': 'in_invoice',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        self.assertEqual(
            invoice.date_due,
            fields.Date.to_date('%s-05-20' % fields.datetime.now().year))

        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term.id,
             'date_invoice': '%s-06-30' % fields.datetime.now().year,
             'type': 'in_invoice',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        self.assertEqual(
            invoice.date_due,
            fields.Date.to_date('%s-08-20' % fields.datetime.now().year))

        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term.id,
             'date_invoice': '%s-11-30' % fields.datetime.now().year,
             'type': 'in_invoice',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        self.assertEqual(
            invoice.date_due,
            fields.Date.to_date('%s-02-20' % (fields.datetime.now().year + 1)))

        with self.assertRaises(exceptions.ValidationError):
            self.payment_term.line_ids = [
                (0, 0, {
                    'value': 'percent', 'value_amount': 30.0, 'sequence': 5,
                    'days': 0, 'option': 'day_after_invoice_date'})
            ]
