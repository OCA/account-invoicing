# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.sale.tests.test_sale_common import TestSale


class TestInvoiceSplitRefunds(TestSale):

    def setUp(self):
        super(TestInvoiceSplitRefunds, self).setUp()

        receivable_acc = self.env['account.account'].search(
            [('internal_type', '=', 'receivable')],
            limit=1
        )
        customer = self.env['res.partner'].create({
            'name': 'Customer',
            'email': 'customer@example.com',
            'property_account_receivable_id': receivable_acc.id,
        })

        self.delivery_product = self.env.ref('product.product_delivery_01')

        self.sale_order = self.env['sale.order'].create({
            'partner_id': customer.id,
            'pricelist_id': self.env.ref('product.list0').id,
        })
        self.sale_order_line = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'name': self.delivery_product.name,
            'product_id': self.delivery_product.id,
            'product_uom_qty': 5,
            'product_uom': self.delivery_product.uom_id.id,
            'price_unit': self.delivery_product.list_price
        })
        self.sale_order.action_confirm()

        self.delivery_picking = self.sale_order.picking_ids
        self.delivery_picking.force_assign()
        self.delivery_picking.pack_operation_product_ids.write({'qty_done': 5})
        self.delivery_picking.do_new_transfer()

    def test_account_invoice_split_refunds(self):
        invoice_id = self.sale_order.action_invoice_create()
        self.invoice = self.env['account.invoice'].browse(invoice_id)
        self.invoice.action_invoice_open()

        return_wiz = self.env['stock.return.picking'].with_context(
            active_ids=self.delivery_picking.ids,
            active_id=self.delivery_picking.id
        ).create({})
        return_wiz.product_return_moves.write({
            'quantity': 2,
            'to_refund_so': True
        })
        return_id = return_wiz.create_returns()['res_id']
        return_picking = self.env['stock.picking'].browse(return_id)
        return_picking.force_assign()
        return_picking.pack_operation_product_ids.write({'qty_done': 2})
        return_picking.do_new_transfer()

        self.assertEqual(self.sale_order_line.qty_delivered, 3)
        self.assertEqual(self.sale_order_line.qty_invoiced, 5)

        service_product = self.env.ref('product.service_order_01')

        sale_order_line_2 = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'name': service_product.name,
            'product_id': service_product.id,
            'product_uom_qty': 6,
            'product_uom': service_product.uom_id.id,
            'price_unit': service_product.list_price
        })
        self.assertEqual(sale_order_line_2.qty_invoiced, 0)
        self.assertEqual(sale_order_line_2.qty_to_invoice, 6)
        create_invoice_wiz = self.env['sale.advance.payment.inv'].with_context(
            active_ids=self.sale_order.ids, active_id=self.sale_order.id
        ).create({})
        self.assertEqual(
            create_invoice_wiz.advance_payment_method, 'all_split'
        )
        create_invoice_wiz.create_invoices()
        self.assertEqual(len(self.sale_order.invoice_ids), 3)

        new_refund = self.sale_order.invoice_ids.filtered(
            lambda i: i.type == 'out_refund')
        new_invoice = self.sale_order.invoice_ids - new_refund - self.invoice

        self.assertEqual(
            new_refund.invoice_line_ids.product_id, self.delivery_product
        )
        # As we invoiced 5 and returned 2, we must refund 2
        self.assertEqual(new_refund.invoice_line_ids.quantity, 2)
        self.assertEqual(
            new_invoice.invoice_line_ids.product_id, service_product
        )

        self.assertEqual(new_invoice.invoice_line_ids.quantity, 6)

    def test_invoice_without_refunds(self):
        create_invoice_wiz = self.env['sale.advance.payment.inv'].with_context(
            active_ids=self.sale_order.ids, active_id=self.sale_order.id
        ).create({})
        create_invoice_wiz.create_invoices()
        self.assertEqual(len(self.sale_order.invoice_ids), 1)
