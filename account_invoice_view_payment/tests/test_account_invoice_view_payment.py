# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestAccountInvoiceViewPayment(TransactionCase):
    """
        Tests for Account Invoice View Payment.
    """
    def setUp(self):
        super(TestAccountInvoiceViewPayment, self).setUp()
        self.par_model = self.env['res.partner']
        self.acc_model = self.env['account.account']
        self.inv_model = self.env['account.invoice']
        self.inv_line_model = self.env['account.invoice.line']
        self.pay_model = self.env['account.payment']
        self.reg_pay_model = self.env['account.register.payments']

        self.cash = self.env['account.journal'].create(
            {'name': 'Cash Test', 'type': 'cash'})
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in")

        self.partner1 = self._create_partner()

        self.invoice_account = self.acc_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1)

        self.invoice_line1 = self._create_inv_line(self.invoice_account.id)
        self.invoice_line2 = self.invoice_line1.copy()

        self.invoice1 = self._create_invoice(self.partner1, self.invoice_line1)
        self.invoice2 = self._create_invoice(self.partner1, self.invoice_line2)

    def _create_partner(self):
        partner = self.par_model.create({
            'name': 'Test Partner',
            'supplier': True,
            'company_type': 'company',
        })
        return partner

    def _create_inv_line(self, account_id):
        inv_line = self.inv_line_model.create({
            'name': 'test invoice line',
            'account_id': account_id,
            'quantity': 1.0,
            'price_unit': 3.0,
            'product_id': self.env.ref('product.product_product_8').id
        })
        return inv_line

    def _create_invoice(self, partner, inv_line):
        invoice = self.inv_model.create({
            'partner_id': partner.id,
            'invoice_line_ids': [(4, inv_line.id)],
        })
        return invoice

    def test_account_invoice_view_payment_wz1(self):
        self.invoice1.invoice_validate()
        wiz1 = self.pay_model.with_context(
            default_invoice_ids=[self.invoice1.id],
            active_model='account.invoice'
        ).create({'journal_id': self.cash.id,
                  'payment_method_id': self.payment_method_manual_in.id,
                  'amount': self.invoice2.amount_total,
                  'payment_type': 'inbound',
                  })

        res1 = wiz1.post_and_open_payment()

        self.assertDictContainsSubset(
            {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'account.payment',
            },
            res1,
            'There was an error and the view couldn\'t be opened.'
        )

        res2 = self.invoice1.action_view_payments()

        self.assertDictContainsSubset(
            {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'account.payment',
            },
            res2,
            'There was an error and the invoice couldn\'t be paid.'
        )

    def test_account_invoice_view_payment_wiz2(self):
        self.invoice2.invoice_validate()
        wiz2 = self.reg_pay_model.with_context(
            active_ids=[self.invoice2.id],
            active_model='account.invoice'
        ).create({'journal_id': self.cash.id,
                  'payment_method_id': self.payment_method_manual_in.id,
                  'amount': self.invoice2.amount_total,
                  })

        res3 = wiz2.create_payment_and_open()

        self.assertDictContainsSubset(
            {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'account.payment',
            },
            res3,
            'There was an error and the two invoices were not merged.'
        )
