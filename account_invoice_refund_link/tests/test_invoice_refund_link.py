# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.addons.account_invoice_refund_link import post_init_hook


class TestInvoiceRefundLink(TransactionCase):
    filter_refund = 'refund'

    def setUp(self, *args, **kwargs):
        super(TestInvoiceRefundLink, self).setUp(*args, **kwargs)
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        default_invoice_account = self.env['account.account'].search([
            ('internal_type', '=', 'receivable'),
            ('deprecated', '=', False),
        ])[0]
        default_line_account = self.env['account.account'].search([
            ('internal_type', '=', 'other'),
            ('deprecated', '=', False),
        ])[0]
        self.invoice_lines = [(0, False, {
            'name': 'Test description #1',
            'account_id': default_line_account.id,
            'quantity': 1.0,
            'price_unit': 100.0,
        }), (0, False, {
            'name': 'Test description #2',
            'account_id': default_line_account.id,
            'quantity': 2.0,
            'price_unit': 25.0,
        })]
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'type': 'out_invoice',
            'account_id': default_invoice_account.id,
            'invoice_line_ids': self.invoice_lines,
        })
        self.invoice.signal_workflow('invoice_open')
        self.refund_reason = 'The refund reason'
        self.env['account.invoice.refund'].with_context(
            active_ids=self.invoice.ids).create({
                'filter_refund': self.filter_refund,
                'description': self.refund_reason,
            }).invoice_refund()

    def test_refund_link(self):
        refund = self.invoice.refund_invoice_ids[0]
        self.assertEqual(refund.refund_reason, self.refund_reason)
        self.assertEqual(refund.origin_invoice_ids[0], self.invoice)
        self.assertEqual(len(self.invoice.invoice_line_ids),
                         len(self.invoice_lines))
        self.assertEqual(len(refund.invoice_line_ids),
                         len(self.invoice_lines))
        self.assertTrue(refund.invoice_line_ids[0].origin_line_ids)
        self.assertEqual(self.invoice.invoice_line_ids[0],
                         refund.invoice_line_ids[0].origin_line_ids[0])
        self.assertTrue(refund.invoice_line_ids[1].origin_line_ids)
        self.assertEqual(self.invoice.invoice_line_ids[1],
                         refund.invoice_line_ids[1].origin_line_ids[0])

    def test_post_init_hook(self):
        refund = self.invoice.refund_invoice_ids[0]
        refund.write({
            'origin_invoice_ids': [(5, False, False)],
        })
        self.assertFalse(refund.origin_invoice_ids)
        post_init_hook(self.env.cr, None)
        self.refund_reason = 'Auto'
        self.test_refund_link()


class TestInvoiceRefundCancelLink(TestInvoiceRefundLink):
    filter_refund = 'cancel'


class TestInvoiceRefundModifyLink(TestInvoiceRefundLink):
    filter_refund = 'modify'
