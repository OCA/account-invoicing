# -*- coding: utf-8 -*-
from openerp.tests.common import HttpCase


class AccountInvoiceForceNumberTestCase(HttpCase):

    def test_force_number(self):
        # in order to test the correct assignment of the internal_number
        # I create a customer invoice.

        invoice_line_data = [
            (0, 0, {
                'product_id': self.env.ref('product.product_product_3').id,
                'quantity': 1.0,
                'account_id': self.env['account.account'].search(
                    [('user_type_id', '=', self.env.ref(
                        'account.data_account_type_revenue').id)],
                    limit=1).id,
                'name': '[PCSC234] PC Assemble SC234',
                'price_unit': 450.00
                })
        ]

        self.account_invoice_customer0 = self.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': self.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': self.env.ref('base.res_partner_12').id,
            'account_id': self.env['account.account'].search(
                [('user_type_id', '=', self.env.ref(
                    'account.data_account_type_receivable').id)],
                limit=1).id,
            'invoice_line_ids': invoice_line_data,
            'internal_number': '0001',
        })

        # I validate the invoice
        self.account_invoice_customer0.signal_workflow('invoice_open')

        # I check that the invoice number is the one we expect
        assert (
            self.account_invoice_customer0.number == '0001'), "Wrong number"
