# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp.tests import common


class TestSaleOrderInvoice(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderInvoice, self).setUp()
        self.year = datetime.now().year
        self.bank = self.env['res.partner.bank'].create({
            'state': 'bank',
            'acc_number': 12345678901234,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'customer': True,
            'default_company_bank_id': self.bank.id
        })
        self.account = self.env['account.account'].search(
            [('type', '=', 'receivable'), ('currency_id', '=', False)],
            limit=1)[0]

        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.list0 = self.ref('product.list0')
        product = self.env['product.product']
        self.product_test = product.create({
            'name': 'Test Product',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'lst_price': 11.55})
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line':
            [(0, 0, {
                'name': 'Demo Product',
                'product_id': self.product_test.id,
                'product_uom_qty': 2,
                'product_uom': self.product_test.uom_id.id,
                'price_unit': self.product_test.lst_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        })

        self.picking_out_1 = self.env['stock.picking'].create({
            'picking_type_id': self.ref('stock.picking_type_out')})

        self.ModelDataObj = self.env['ir.model.data']
        self.stock_location = self.ModelDataObj.xmlid_to_res_id(
            'stock.stock_location_stock')

    def test_invoice_default_company_bank_sale_order(self):
        context = {"active_model": 'sale.order', "active_ids": [
            self.sale_order.id], "active_id": self.sale_order.id}
        self.sale_order.with_context(context).action_button_confirm()
        payment = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'all',
            'product_id': self.product_test.id,
        })
        payment.with_context(context).create_invoices()
        self.assertEqual(self.sale_order.invoice_ids.partner_bank_id.
                         acc_number,
                         self.partner.default_company_bank_id.acc_number)
