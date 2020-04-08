# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .. import post_init_hook
from odoo.addons.account.tests.account_test_no_chart \
    import TestAccountNoChartCommon


class TestInvoiceRefundLinkBase(TestAccountNoChartCommon):
    filter_refund = 'refund'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        super().setUpAdditionalAccounts()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'customer': True,
            'property_account_receivable_id': cls.account_receivable.id,
        })
        cls.invoice_lines = [(0, False, {
            'name': 'Test description #1',
            'account_id': cls.account_income.id,
            'quantity': 1.0,
            'price_unit': 100.0,
        }), (0, False, {
            'name': 'Test description #2',
            'account_id': cls.account_income.id,
            'quantity': 2.0,
            'price_unit': 25.0,
        })]
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'invoice_line_ids': cls.invoice_lines,
        })
        cls.invoice.action_invoice_open()
        cls.refund_reason = 'The refund reason'
        cls.env['account.invoice.refund'].with_context(
            active_ids=cls.invoice.ids).create({
                'filter_refund': cls.filter_refund,
                'description': cls.refund_reason,
            }).invoice_refund()

    def _test_refund_link(self):
        self.assertTrue(self.invoice.refund_invoice_ids)
        refund = self.invoice.refund_invoice_ids[0]
        self.assertEqual(refund.refund_reason, self.refund_reason)
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


class TestInvoiceRefundLink(TestInvoiceRefundLinkBase):
    def test_post_init_hook(self):
        self.assertTrue(self.invoice.refund_invoice_ids)
        refund = self.invoice.refund_invoice_ids[0]
        refund.invoice_line_ids.write({
            'origin_line_ids': [(5, False, False)],
        })
        self.assertFalse(refund.mapped('invoice_line_ids.origin_line_ids'))
        post_init_hook(self.env.cr, None)
        self.refund_reason = 'The refund reason'
        self._test_refund_link()

    def test_refund_link(self):
        self._test_refund_link()

    def test_invoice_copy(self):
        refund = self.invoice.refund_invoice_ids[0]
        self.invoice.copy()
        self.assertEqual(
            refund.mapped('invoice_line_ids.origin_line_ids'),
            self.invoice.mapped('invoice_line_ids'),
        )

    def test_refund_copy(self):
        refund = self.invoice.refund_invoice_ids[0]
        refund.copy()
        self.assertEqual(
            self.invoice.mapped('invoice_line_ids.refund_line_ids'),
            refund.mapped('invoice_line_ids'),
        )


class TestInvoiceRefundCancelLink(TestInvoiceRefundLinkBase):
    filter_refund = 'cancel'

    def test_refund_link(self):
        self._test_refund_link()


class TestInvoiceRefundModifyLink(TestInvoiceRefundLinkBase):
    filter_refund = 'modify'

    def test_refund_link(self):
        self._test_refund_link()
