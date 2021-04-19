# Copyright 2019 Creu Blanca
# Copyright 2021 FactorLibre - César Castañón <cesar.castanon@factorlibre.com>
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
        cls.tax = cls.env['account.tax'].create({
            'name': 'T1',
            'amount': 21,
            'price_include': True
        })
        default_line_account = cls.env['account.account'].search([
            ('internal_type', '=', 'other'),
            ('deprecated', '=', False),
            ('company_id', '=', cls.env.user.company_id.id),
        ], limit=1)
        cls.invoice_lines = [(0, False, {
            'name': 'Test description #1',
            'account_id': default_line_account.id,
            'quantity': 5.0,
            'invoice_line_tax_ids': [(6, 0, [cls.tax.id])],
            'price_unit': 100.0,
        }), (0, False, {
            'name': 'Test description #2',
            'account_id': default_line_account.id,
            'quantity': 2.0,
            'invoice_line_tax_ids': [(6, 0, [cls.tax.id])],
            'price_unit': 25.0,
        })]
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'invoice_line_ids': cls.invoice_lines,
        })
        cls.invoice.action_invoice_open()
        cls.refund_reason = 'The refund reason'
        acc_inv_ref_model = cls.env['account.invoice.refund']
        fields = [name for name, _ in acc_inv_ref_model._fields.items()]
        default_vals = acc_inv_ref_model.with_context(
            active_ids=[cls.invoice.id],
            active_id=cls.invoice.id
        ).default_get(fields)
        default_vals.update({
            'filter_refund': 'refund_lines',
            'description': cls.refund_reason,
        })
        cls.refund = cls.env['account.invoice.refund'].with_context(
            active_ids=[cls.invoice.id],
            active_id=cls.invoice.id).create(default_vals)
        cls.refund.update({
            'line_ids': [
                (6, 0, cls.refund.selectable_invoice_lines_ids[0].ids)
            ]
        })

    def test_refund_line_unmodified(self):
        self.refund.invoice_refund()
        self.assertTrue(self.invoice.refund_invoice_ids)
        refund = self.invoice.refund_invoice_ids[0]
        self.assertEqual(
            len(refund.invoice_line_ids),
            1,
            "The line in the refund invoice is missing"
        )
        invoice_line = self.invoice.invoice_line_ids[0]
        refund_invoice_line = refund.invoice_line_ids[0]
        self.assertEqual(
            refund.invoice_line_ids[0].name,
            invoice_line.name,
            "The refund invoice is not properly linked to it's parent invoice"
        )
        fields_to_check = [
            'name', 'account_id', 'product_id', 'quantity', 'price_unit',
            'discount', 'invoice_line_tax_ids', 'price_subtotal',
        ]
        for attr in fields_to_check:
            self.assertEqual(
                getattr(refund_invoice_line, attr),
                getattr(invoice_line, attr),
                "Copy data didn't work. Values between invoice line and refund "
                "line aren't equal"
            )

    def test_refund_line_mod_qty(self):
        self.refund.line_ids[0].update({
            'quantity': 3
        })
        self.refund.invoice_refund()
        self.assertEqual(
            self.invoice.invoice_line_ids[0].quantity,
            5,
            "Quantity should have been updated "
        )
        refund_inv_id = self.invoice.refund_invoice_ids[0]
        self.assertEqual(
            refund_inv_id.invoice_line_ids[0].quantity,
            3,
            "Quantity should have been updated "
        )

    def test_refund_line_mod_discount(self):
        self.refund.line_ids[0].update({
            'discount': 10.0
        })
        self.refund.invoice_refund()
        self.assertEqual(
            self.invoice.invoice_line_ids[0].discount,
            0,
            "Quantity should have been updated "
        )
        refund_inv_id = self.invoice.refund_invoice_ids[0]
        self.assertEqual(
            refund_inv_id.invoice_line_ids[0].discount,
            10.0,
            "Quantity should have been updated "
        )
