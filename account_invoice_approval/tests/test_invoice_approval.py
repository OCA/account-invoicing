# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInvoiceApproval(TransactionCase):
    def setUp(self):
        super(TestInvoiceApproval, self).setUp()
        self.company1 = self.env.ref('base.main_company')

        self.acc_type = self.env.ref('account.data_account_type_receivable')
        self.partner = self.env.ref('base.res_partner_1')
        self.partner2 = self.env.ref('base.res_partner_2')
        self.account = self.env['account.account'].search([('user_type_id', '=', self.acc_type.id)], limit=1)
        self.admin = self.env.ref('base.user_root')

        # Flow
        self.flow1 = self.env['account.invoice.approval.flow'].create({
            'domain': '[("partner_id", "=", %s)]' % self.partner.id,
            'sequence': 0,
            'step_ids': [
                (0, 0, {'user_ids': [self.admin.id]})
            ]
        })

    def test_in_domain(self):
        invoice = self.env['account.invoice'].create({
            'type': 'out_invoice',
            'name': 'Invoice #1',
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'invoice_line_ids': [
                (0, 0, {'name': '123', 'price_unit': 100, 'quantity': 1, 'account_id': self.account.id}),
            ]
        })
        invoice.submit_for_review()
        self.assertEqual(invoice.state, 'to_review')

    def test_not_in_domain(self):
        invoice = self.env['account.invoice'].create({
            'type': 'in_invoice',
            'name': 'Invoice #2',
            'partner_id': self.partner2.id,
            'account_id': self.account.id,
            'invoice_line_ids': [
                (0, 0, {'name': '123', 'price_unit': 100, 'quantity': 1, 'account_id': self.account.id}),
            ]
        })
        invoice.submit_for_review()
        self.assertEqual(invoice.state, 'approved')
