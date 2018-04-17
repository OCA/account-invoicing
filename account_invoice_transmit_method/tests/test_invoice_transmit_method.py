# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceTransmitMethod(TransactionCase):

    def test_create_invoice(self):
        post_method = self.env.ref('account_invoice_transmit_method.post')
        partner1 = self.env['res.partner'].create({
            'is_company': True,
            'name': 'Old School Company',
            'customer': True,
            'customer_invoice_transmit_method_id': post_method.id,
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
        self.assertEqual(inv1.transmit_method_id, post_method)
