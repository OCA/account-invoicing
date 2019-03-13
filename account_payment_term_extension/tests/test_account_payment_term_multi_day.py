import odoo.tests.common as common
from odoo import fields


class TestAccountPaymentTermMultiDay(common.TransactionCase):

    def setUp(self):
        super(TestAccountPaymentTermMultiDay, self).setUp()
        self.payment_term_model = self.env['account.payment.term']
        self.invoice_model = self.env['account.invoice']
        journal_model = self.env['account.journal']
        self.journal = journal_model.search([('type', '=', 'purchase')])
        self.partner = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_5')
        self.prod_account = self.env.ref('account.demo_coffee_machine_account')
        self.inv_account = self.env.ref('account.demo_sale_of_land_account')
        self.payment_term_0_day_5 = self.payment_term_model.create(
            {"name": "Normal payment in day 5",
             "active": True,
             "line_ids": [(0, 0, {'value': 'balance',
                                  'days': 5,
                                  'payment_days': '5',
                                  'day_of_the_month': 31,
                                  })],
             })
        self.payment_term_0_days_5_10 = self.payment_term_model.create(
            {"name": "Payment for days 5 and 10",
             "active": True,
             "line_ids": [(0, 0, {'value': 'balance',
                                  'days': 0,
                                  'payment_days': '5,10',
                                  })],
             })
        self.payment_term_0_days_15_20_then_5_10 = \
            self.payment_term_model.create(
                {"name": "Payment for days 15 and 20 then 5 and 10",
                 "active": True,
                 "sequential_lines": True,
                 "line_ids": [(0, 0, {'value': 'percent',
                                      'value_amount': 50.0,
                                      'days': 0,
                                      'payment_days': '15,20',
                                      'option': 'day_after_invoice_date',
                                      }),
                              (0, 0, {'value': 'balance',
                                      'days': 0,
                                      'payment_days': '10-5',
                                      'option': 'day_after_invoice_date',
                                      })],
                 })

    def test_invoice_normal_payment_term(self):
        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term_0_day_5.id,
             'date_invoice': '%s-01-01' % fields.datetime.now().year,
             'name': 'Invoice for normal payment on day 5',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        for line in invoice.move_id.line_ids:
            if line.name == invoice.name and line.date_maturity:
                self.assertEqual(
                    fields.Date.to_string(line.date_maturity),
                    '%s-02-05' % fields.datetime.now().year,
                    "Incorrect due date for invoice with normal payment day "
                    "on 5")

    def test_invoice_multi_payment_term_day_1(self):
        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term_0_days_5_10.id,
             'date_invoice': '%s-01-01' % fields.datetime.now().year,
             'name': 'Invoice for payment on days 5 and 10 (1)',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        for line in invoice.move_id.line_ids:
            if line.name == invoice.name and line.date_maturity:
                self.assertEqual(
                    fields.Date.to_string(line.date_maturity),
                    '%s-01-05' % fields.datetime.now().year,
                    "Incorrect due date for invoice with payment days on 5 "
                    "and 10 (1)")

    def test_invoice_multi_payment_term_day_6(self):
        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term_0_days_5_10.id,
             'date_invoice': '%s-01-06' % fields.datetime.now().year,
             'name': 'Invoice for payment on days 5 and 10 (2)',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        for line in invoice.move_id.line_ids:
            if line.name == invoice.name and line.date_maturity:
                self.assertEqual(
                    fields.Date.to_string(line.date_maturity),
                    '%s-01-10' % fields.datetime.now().year,
                    "Incorrect due date for invoice with payment days on 5 "
                    "and 10 (2)")

    def test_invoice_multi_payment_term_sequential_day_1(self):
        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term_0_days_15_20_then_5_10.id,
             'date_invoice': '%s-01-01' % fields.datetime.now().year,
             'name': 'Invoice for payment on days 15 and 20 then 5 and 10 (1)',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        dates_maturity = []
        for line in invoice.move_id.line_ids:
            if line.name == invoice.name and line.date_maturity:
                dates_maturity.append(line.date_maturity)
        dates_maturity.sort()
        self.assertEqual(
            fields.Date.to_string(dates_maturity[0]),
            '%s-01-15' % fields.datetime.now().year,
            "Incorrect due date for invoice with payment days on "
            "15 and 20 then 5 and 10 (1)")
        self.assertEqual(
            fields.Date.to_string(dates_maturity[1]),
            '%s-02-05' % fields.datetime.now().year,
            "Incorrect due date for invoice with payment days on "
            "15 and 20 then 5 and 10 (1)")

    def test_invoice_multi_payment_term_sequential_day_18(self):
        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term_0_days_15_20_then_5_10.id,
             'date_invoice': '%s-01-18' % fields.datetime.now().year,
             'name': 'Invoice for payment on days 15 and 20 then 5 and 10 (2)',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        dates_maturity = []
        for line in invoice.move_id.line_ids:
            if line.name == invoice.name and line.date_maturity:
                dates_maturity.append(line.date_maturity)
        dates_maturity.sort()
        self.assertEqual(
            fields.Date.to_string(dates_maturity[0]),
            '%s-01-20' % fields.datetime.now().year,
            "Incorrect due date for invoice with payment days on "
            "15 and 20 then 5 and 10 (2)")
        self.assertEqual(
            fields.Date.to_string(dates_maturity[1]),
            '%s-02-05' % fields.datetime.now().year,
            "Incorrect due date for invoice with payment days on "
            "15 and 20 then 5 and 10 (2)")

    def test_invoice_multi_payment_term_sequential_day_25(self):
        invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.partner.id,
             'account_id': self.inv_account.id,
             'payment_term_id': self.payment_term_0_days_15_20_then_5_10.id,
             'date_invoice': '%s-01-25' % fields.datetime.now().year,
             'name': 'Invoice for payment on days 15 and 20 then 5 and 10 (3)',
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Test',
                                          'quantity': 10.0,
                                          'price_unit': 100.00,
                                          'account_id': self.prod_account.id,
                                          })],
             })
        invoice.action_invoice_open()
        dates_maturity = []
        for line in invoice.move_id.line_ids:
            if line.name == invoice.name and line.date_maturity:
                dates_maturity.append(line.date_maturity)
        dates_maturity.sort()
        self.assertEqual(
            fields.Date.to_string(dates_maturity[0]),
            '%s-02-15' % fields.datetime.now().year,
            "Incorrect due date for invoice with payment days on "
            "15 and 20 then 5 and 10 (3)")
        self.assertEqual(
            fields.Date.to_string(dates_maturity[1]),
            '%s-03-05' % fields.datetime.now().year,
            "Incorrect due date for invoice with payment days on "
            "15 and 20 then 5 and 10 (3)")

    def test_decode_payment_days(self):
        expected_days = [5, 10]
        model = self.env['account.payment.term.line']
        self.assertEqual(expected_days, model._decode_payment_days('5,10'))
        self.assertEqual(expected_days, model._decode_payment_days('5-10'))
        self.assertEqual(expected_days, model._decode_payment_days('5 10'))
        self.assertEqual(expected_days, model._decode_payment_days('10,5'))
        self.assertEqual(expected_days, model._decode_payment_days('10-5'))
        self.assertEqual(expected_days, model._decode_payment_days('10 5'))
        self.assertEqual(expected_days, model._decode_payment_days('5, 10'))
        self.assertEqual(expected_days, model._decode_payment_days('5 - 10'))
        self.assertEqual(expected_days, model._decode_payment_days('5    10'))
