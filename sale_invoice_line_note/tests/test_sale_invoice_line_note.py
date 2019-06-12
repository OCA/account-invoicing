# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestSaleInvoiceLineNote(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.env.ref('base.res_partner_12').id,
        })
        product = cls.env.ref('product.product_product_1')
        product.invoice_policy = 'order'
        cls.env['sale.order.line'].create([{
            'order_id': cls.sale_order.id,
            'product_id': product.id,
            'name': product.name,
            'price_unit': 1.0,
            'product_uom_qty': 1.0,
        }, {
            'order_id': cls.sale_order.id,
            'display_type': 'line_note',
            'name': 'Test sale order line note',
            'sequence': 12,
        }])
        cls.sale_order.action_confirm()

    def test_sale_note_to_invoice(self):
        wizard = self.env['sale.advance.payment.inv'].with_context(
            active_ids=self.sale_order.ids).create({
                'advance_payment_method': 'all',
            })
        self.assertTrue(wizard.copy_notes_to_invoice)
        wizard.create_invoices()
        invoice = self.sale_order.invoice_ids
        self.assertEqual(
            len(self.sale_order.order_line), len(invoice.invoice_line_ids)
        )
        invoice_line_note = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == 'line_note'
        )
        self.assertEqual(invoice_line_note.name, 'Test sale order line note')
        self.assertEqual(invoice_line_note.sequence, 12)

    def test_sale_note_no_copy(self):
        wizard = self.env['sale.advance.payment.inv'].with_context(
            active_ids=self.sale_order.ids).create({
            'advance_payment_method': 'all',
        })
        wizard.copy_notes_to_invoice = False
        wizard.create_invoices()
        invoice = self.sale_order.invoice_ids
        invoice_line_note = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == 'line_note'
        )
        self.assertFalse(invoice_line_note)
