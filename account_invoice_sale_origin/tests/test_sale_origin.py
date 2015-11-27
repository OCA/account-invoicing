# -*- coding: utf-8 -*-
# © 2015 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestSaleOrigin(TransactionCase):

    def setUp(self):
        """Setup a Sale Order with 1 line.
        """
        super(TestSaleOrigin, self).setUp()

        customer = self.env.ref('base.res_partner_3')
        product = self.env.ref('product.product_product_9')

        self.sale_order = self.env['sale.order'].create({
            'partner_id': customer.id,
            'order_policy': 'manual',
        })
        self.sale_order_line = self.env['sale.order.line'].create({
            'name': '/',
            'order_id': self.sale_order.id,
            'product_id': product.id,
        })

    def test_propagate_value(self):
        """Test that origin value is correctly propagated to the invoice
        """
        self.sale_order.action_button_confirm()
        self.sale_order.action_invoice_create()
        invoice = self.sale_order.invoice_ids
        self.assertEqual(1, len(invoice))
        invoice_line = invoice.mapped('invoice_line')
        self.assertEqual(1, len(invoice_line))
        self.assertEqual(self.sale_order.name, invoice_line.origin)
