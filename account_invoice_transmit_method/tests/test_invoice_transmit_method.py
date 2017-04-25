# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestAccountInvoiceTransmitMethod(TransactionCase):

    def test_create_invoice(self):
        post_method = self.env.ref('account_invoice_transmit_method.post')
        partner1 = self.env['res.partner'].create({
            'is_company': True,
            'name': 'Old School Company',
            'customer': True,
            'customer_invoice_transmit_method_id': post_method.id,
            })
        inv1 = self.env['account.invoice'].create({
            'partner_id': partner1.id,
            'type': 'out_invoice',
            'journal_id': self.env.ref('account.sales_journal').id,
            'account_id': self.env.ref('account.a_recv').id,
            })
        self.assertEqual(inv1.transmit_method_id, post_method)
