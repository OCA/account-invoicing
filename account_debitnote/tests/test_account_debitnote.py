
from datetime import date
from odoo.tests import common


class TestAccountDebitNote(common.TransactionCase):

    def setUp(self):
        super(TestAccountDebitNote, self).setUp()
        #  Create Invoice
        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceDebitnote = self.env['account.invoice.debitnote']
        self.partner = self.env.ref("base.res_partner_1")
        self.account = self.env.ref("account.a_recv")
        self.product = self.env.ref("product.product_product_1")
        self.period = self.env.ref("account.period_1")
        self.sales_journal = self.env.ref("account.sales_journal")
        self.sale_debitnote_journal = self.env.ref(
            'account_debitnote.central_contract_clearing_journal')
        self.company = self.env.ref("base.main_company")
        self.account_invoice_debitnote = self.AccountInvoiceDebitnote.create({
            'date': date.today(),
            'period': self.period.id,
            'description': 'Test Debit Note',
            'journal_id': self.sale_debitnote_journal.id
        })

    def test_invoice_debitnote(self):
        print('---------------------------------')
        x = 1/0
        invoice_line_val = {
            'name': 'iMac',
            'product_id': self.product.id,
            'quantity': 5,
            'price_unit': 1799.00,
        }

        self.invoice_id = self.AccountInvoice.create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'journal_id': self.sales_journal.id,
            'company_id': self.company.id,
            'invoice_line': [(0, 0, invoice_line_val)],
        })
        self.invoice_id.action_invoice_open()
        self.assertEqual(self.invoice_id.state, 'open',
                         'Invoice not validated.')
        self.assertNotEqual(self.invoice_id.state, 'draft',
                            'Cannot create debit note for draft invoice.')

        self.assertNotEqual(self.invoice_id.state, 'proforma2',
                            'Cannot create debit note for proforma invoice.')

        self.assertNotEqual(self.invoice_id.state, 'cancel',
                            'Cannot create debit note for cancelled invoice.')

        ctx = self.env.context.copy()
        ctx.update({'active_ids': [self.invoice_id.id],
                    'active_id': self.invoice_id.id})
        self.debitnote = self.account_invoice_debitnote.\
            with_context(ctx).invoice_debitnote()
        self.assertNotEqual(self.invoice_id.debit_invoice_ids, False,
                            'Debitnote not created.')
