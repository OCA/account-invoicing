# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase
from lxml import html


class TestAccountInvoiceGroupPicking(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceGroupPicking, cls).setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'Test category',
            'type': 'normal',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'categ_id': cls.category.id,
            'default_code': 'TESTPROD01',
            'invoice_policy': 'delivery',
        })
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Pricelist Test',
            'item_ids': [(0, 0, {
                'compute_price': 'formula',
                'base': 'list_price',  # based on public price
                'price_discount': 10,
            })]
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner for test',
            'property_product_pricelist': cls.pricelist.id,
        })
        cls.sale = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'product_uom_qty': 2,
                    'product_uom': cls.product.uom_id.id,
                    'price_unit': 100.0,
                })]
        })

    def test_account_invoice_group_picking(self):
        # confirm quotation
        self.sale.action_confirm()
        # deliver lines
        for line in self.sale.order_line:
            line.qty_delivered = 2
        self.sale.picking_ids[:1].action_done()
        # create another sale
        self.sale2 = self.sale.copy()
        self.sale2.order_line[:1].product_uom_qty = 4
        self.sale2.order_line[:1].price_unit = 50.0
        # confirm new quotation
        self.sale2.action_confirm()
        # deliver lines
        for line in self.sale2.order_line:
            line.qty_delivered = 4
        self.sale2.picking_ids[:1].action_done()
        sales = self.sale | self.sale2
        # invoice sales
        inv_id = sales.action_invoice_create()
        invoice = self.env['account.invoice'].browse(inv_id)
        content = html.document_fromstring(
            self.env['report'].get_html(invoice, 'account.report_invoice')
        )
        tbody = content.xpath("//tbody[@class='invoice_tbody']")
        tbody = [html.tostring(line).strip() for line in tbody]
        # information about sales is printed
        self.assertTrue('Order: %s' % self.sale.name in tbody[0])
        self.assertTrue('Order: %s' % self.sale2.name in tbody[0])
        # information about pickings is printed
        self.assertTrue(self.sale.picking_ids[:1].name in tbody[0])
        self.assertTrue(self.sale2.picking_ids[:1].name in tbody[0])
