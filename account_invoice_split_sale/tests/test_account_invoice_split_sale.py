# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceSplitSale(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceSplitSale, self).setUp()
        self.SaleOrderObj = self.env['sale.order']
        self.SplitObj = self.env['account.invoice.split']

        self.partner = self.env.ref('base.res_partner_1')
        self.product_delivery = self.env.ref('product.product_order_01')
        self.pricelist = self.env.ref('product.list0')

    def create_sale_order(self):
        product = self.product_delivery
        return self.SaleOrderObj.create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.pricelist.id,
            'picking_policy': 'direct',
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': 6,
                    'product_uom': product.uom_id.id,
                    'price_unit': product.list_price,
                })
            ]
        })

    def test_01_split_invoice_from_so(self):
        order = self.create_sale_order()
        order.action_confirm()

        order_line = order.order_line[0]
        self.assertEqual(order_line.qty_invoiced, 0)

        order.action_invoice_create()
        self.assertEqual(order_line.qty_invoiced, 6)

        invoices = order.invoice_ids
        self.assertEqual(len(invoices), 1)
        invoice = invoices[0]

        wiz = self.SplitObj.with_context(
            active_ids=[invoice.id]).create({})
        wiz_line = wiz.line_ids[0]
        wiz_line.quantity_to_split = 3

        wiz._split_invoice()
        self.assertEqual(order_line.qty_invoiced, 6)
