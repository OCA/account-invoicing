# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.test_mail.tests.common import MockEmails
from odoo.tests.common import Form, TransactionCase


class TestTransmitInvoiceMail(TransactionCase, MockEmails):

    def test_transmit_email(self):
        method = self.env.ref('account_invoice_transmit_method.mail')
        self.assertTrue(method.send_mail)
        partner1 = self.env['res.partner'].create({
            'is_company': True,
            'name': 'Old School Company',
            'customer': True,
            'customer_invoice_transmit_method_id': method.id,
            'email': 'demo@demo.org'
        })
        account_receivable = self.env['account.account'].create({
            'code': '411ZYX',
            'name': 'Debtors - (test)',
            'reconcile': True,
            'user_type_id':
                self.env.ref('account.data_account_type_receivable').id,
        })
        sale_journal = self.env['account.journal'].create({
            'code': 'XYZZZ',
            'name': 'sale journal (test)',
            'type': 'sale',
        })
        inv1 = self.env['account.invoice'].create({
            'partner_id': partner1.id,
            'type': 'out_invoice',
            'journal_id': sale_journal.id,
            'account_id': account_receivable.id,
        })
        self.env['account.invoice.line'].create({
            'quantity': 1,
            'price_unit': 10,
            'invoice_id': inv1.id,
            'name': 'something',
            'account_id': account_receivable.id,
        })
        self.assertEqual(inv1.transmit_method_id, method)
        inv1.action_invoice_open()
        action = inv1.action_invoice_sent()
        ctx = action['context'].copy()
        ctx.update({
            'active_ids': inv1.ids,
        })
        with Form(
            self.env[action['res_model']].with_context(**ctx)
        ) as composer_form:
            self.assertTrue(composer_form.is_transmit)
            composer_form.is_email = False
            composer_form.is_print = False
            composer = composer_form.save()
            composer.invoice_ids = inv1
            composer.send_and_print_action()
            self.assertEmails(self.env.user.partner_id, inv1.partner_id)
