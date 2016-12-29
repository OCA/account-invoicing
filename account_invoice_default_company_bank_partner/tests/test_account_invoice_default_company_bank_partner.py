# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp.tests import common


class TestAccountInvoice(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        self.year = datetime.now().year
        self.bank = self.env['res.partner.bank'].create({
            'state': 'bank',
            'acc_number': 12345678901234,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'customer': True,
            'default_company_bank_id': self.bank.id
        })
        self.account = self.env['account.account'].search(
            [('type', '=', 'receivable'), ('currency_id', '=', False)],
            limit=1)[0]

    def test_invoice_default_company_bank_partner(self):
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'date_invoice': '%s-01-01' % self.year,
            'type': 'out_invoice',
            'origin': 'TEST1234',
            'invoice_line': [(0, 0, {
                'name': 'Test',
                'account_id': self.account.id,
                'price_unit': 234.56,
                'quantity': 1,
            })],
        })
        invoice_data = self.invoice
        onchange_res = invoice_data.onchange_partner_id(
            invoice_data.type, invoice_data.partner_id.id,
            invoice_data.date_invoice, invoice_data.payment_term.id,
            invoice_data.partner_bank_id.id,
            invoice_data.company_id.id)
        self.assertEqual(onchange_res.get('value').get
                         ('partner_bank_id').acc_number,
                         self.partner.default_company_bank_id.acc_number)
