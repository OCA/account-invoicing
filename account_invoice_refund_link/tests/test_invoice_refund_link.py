# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from .. import post_init_hook


class TestInvoiceRefundLink(common.SavepointCase):
    filter_refund = 'refund'

    @classmethod
    def setUpClass(cls):
        super(TestInvoiceRefundLink, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        default_line_account = cls.env['account.account'].search([
            ('internal_type', '=', 'other'),
            ('deprecated', '=', False),
            ('company_id', '=', cls.env.user.company_id.id),
        ], limit=1)
        cls.invoice_lines = [(0, False, {
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
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'invoice_line_ids': cls.invoice_lines,
        })
        cls.invoice.signal_workflow('invoice_open')
        cls.refund_reason = 'The refund reason'
        cls.env['account.invoice.refund'].with_context(
            active_ids=cls.invoice.ids).create({
                'filter_refund': cls.filter_refund,
                'description': cls.refund_reason,
            }).invoice_refund()

    def test_refund_link(self):
        self.assertTrue(self.invoice.refund_invoice_ids)
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
        self.assertTrue(self.invoice.refund_invoice_ids)
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
