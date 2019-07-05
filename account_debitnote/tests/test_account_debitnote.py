# Copyright 2019 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError, UserError
from datetime import date


class TestAccountDebitNote(TransactionCase):

    def setUp(self):
        super(TestAccountDebitNote, self).setUp()
        self.AccountInvoice = self.env['account.invoice']
        self.AccountJournal = self.env['account.journal']
        self.Wizard = self.env['account.invoice.debitnote']
        self.test_partner = self.env.ref('base.res_partner_12')
        self.test_product = self.env.ref('product.product_product_7')
        self.test_customer_debitnote = self.env['account.journal'].create({
            'name': 'TEST DEBITNOTE',
            'type': 'sale',
            'code': 'TINV',
            'debitnote_sequence': True,
        })

    def call_invoice_debit_note(self, invoice):
        ctx = {'active_id': invoice.id, 'active_ids': [invoice.id]}
        view_id = 'account_debitnote.view_account_invoice_debitnote'
        with Form(self.Wizard.with_context(ctx), view=view_id) as f:
            f.date = date.today()
            f.description = 'Test'
        wizard = f.save()
        wizard.invoice_debitnote()

    def test_1_account_debitnote(self):
        """I create invoice, validate it, and create debit note. I expect,
        - Invoice is open.
        - Debit note is created.
        - debitnote_sequence_id can create yourself after delete.
        """
        with Form(self.AccountInvoice) as f:
            f.partner_id = self.test_partner
            f.type = 'out_invoice'
            with f.invoice_line_ids.new() as line:
                line.product_id = self.test_product
        invoice = f.save()
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, 'open')
        self.call_invoice_debit_note(invoice)
        debit = self.env['account.invoice'].search(
            [('debit_invoice_id', '=', invoice.id)])
        debit.journal_id = self.test_customer_debitnote
        debit.journal_id.debitnote_sequence_id.unlink()
        debit.journal_id.debitnote_sequence = True
        debit.journal_id._compute_debitnote_seq_number_next()
        self.assertEqual(debit.journal_id.debitnote_sequence_number_next, 1)
        debit.journal_id.debitnote_sequence_number_next = 999
        debit.action_invoice_open()
        self.assertEqual(debit.state, 'open')

    def test_2_account_journal(self):
        """I create journal, set type=sale/purchase, and get debitnote_sequence.
        Expect:
        - Journal has created.
        - sequence id and sequence number has created.
         """
        with Form(self.AccountJournal) as j:
            j.name = 'Test Journal'
            j.type = 'sale'
            j.code = 'TINV'
            j.debitnote_sequence = True
        j.save()

    def test_3_Error(self):
        """Create debit note in Credit note, Refund.
        Create debitnote without debitnote_sequence_id. I expect,
        - ValidationError.
        - UserError.
        """
        with Form(self.AccountInvoice) as f:
            f.partner_id = self.test_partner
            f.type = 'out_invoice'
            with f.invoice_line_ids.new() as line:
                line.product_id = self.test_product
        invoice = f.save()
        with self.assertRaises(ValidationError):
            self.call_invoice_debit_note(invoice)

        with Form(self.AccountInvoice) as f:
            f.partner_id = self.test_partner
            f.type = 'out_refund'
            with f.invoice_line_ids.new() as line:
                line.product_id = self.test_product
        creditnote = f.save()
        creditnote.action_invoice_open()
        with self.assertRaises(ValidationError):
            self.call_invoice_debit_note(creditnote)

        with Form(self.AccountInvoice) as f:
            f.partner_id = self.test_partner
            f.type = 'out_invoice'
            f.journal_id = self.test_customer_debitnote
            with f.invoice_line_ids.new() as line:
                line.product_id = self.test_product
        invoice = f.save()
        invoice.action_invoice_open()
        self.call_invoice_debit_note(invoice)
        debit = self.env['account.invoice'].search(
            [('debit_invoice_id', '=', invoice.id)])
        debit.journal_id.debitnote_sequence_id = False
        with self.assertRaises(UserError):
            debit.action_invoice_open()
