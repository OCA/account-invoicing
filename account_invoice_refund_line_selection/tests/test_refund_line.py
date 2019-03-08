# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import common


class TestInvoiceRefundLine(common.SavepointCase):
    filter_refund = 'refund'

    @classmethod
    def setUpClass(cls):
        super(TestInvoiceRefundLine, cls).setUpClass()
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
        cls.invoice.action_invoice_open()
        cls.refund_reason = 'The refund reason'
        cls.refund = cls.env['account.invoice.refund'].with_context(
            active_ids=cls.invoice.ids).create({
                'filter_refund': 'refund_lines',
                'description': cls.refund_reason,
                'line_ids': [(6, 0, cls.invoice.invoice_line_ids[0].ids)]
            })

    def test_refund_line(self):
        self.refund.invoice_refund()
        self.assertTrue(self.invoice.refund_invoice_ids)
        refund = self.invoice.refund_invoice_ids[0]
        self.assertTrue(len(refund.invoice_line_ids), 1)
        self.assertTrue(refund.invoice_line_ids[0].name,
                        self.invoice.invoice_line_ids[0].name)
