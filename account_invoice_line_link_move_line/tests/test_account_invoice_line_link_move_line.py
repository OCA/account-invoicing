# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from ..hooks import post_init_hook


class TestAccountInvoiceLineLinkMoveLine(TransactionCase):
    def _test_account_invoice_flow(self, invoice):
        self.assertEqual(invoice.state, 'draft')
        invoice.signal_workflow('invoice_open')
        move_lines = self.env['account.move.line']
        for line in invoice.invoice_line:
            self.assertTrue(line.move_line_ids & invoice.move_id.line_id)
            move_lines |= line.move_line_ids
        invoice_move_line = invoice.move_id.line_id - move_lines
        self.assertEqual(len(invoice_move_line), 1)
        self.assertEqual(
            sum(move_lines.mapped('credit')), invoice_move_line.debit,
        )
        self.assertEqual(
            sum(move_lines.mapped('debit')), invoice_move_line.credit,
        )

    def test_account_invoice_line_link_move_line(self):
        self._test_account_invoice_flow(self.env.ref('account.demo_invoice_0'))

    def test_account_invoice_line_link_move_line_grouped(self):
        invoice = self.env.ref('account.demo_invoice_0')
        invoice.journal_id.write({'group_invoice_lines': True})
        # duplicate invoice lines
        invoice.mapped('invoice_line').copy()
        self._test_account_invoice_flow(invoice)

    def test_account_invoice_line_link_init_hook(self):
        post_init_hook(self.env.cr, None)
        invoice = self.env.ref('account.invoice_1')
        self.assertTrue(invoice.invoice_line.mapped('move_line_ids'))
