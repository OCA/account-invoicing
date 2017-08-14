# -*- coding: utf-8 -*-
# © 2011 Domsense s.r.l. (<http://www.domsense.com>).
# © 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# © 2015 ACSONE SA/NV (<http://acsone.eu>)
# © 2016 Farid Shahy (<fshahy@gmail.com>)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceShippement(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceShippement, self).setUp()

        self.partner = self.env.ref('base.res_partner_12')
        self.sale_object = self.env['sale.order']
        self.invoice_object = self.env['account.invoice']
        self.stock_picking_object = self.env['stock.picking']

        # products with invoice_policy set to ordered quantities
        self.products_ord = self.env.ref('stock.product_icecream')

        # products with invoice_policy set to delivered quantities
        self.products_del = self.env.ref('product.product_product_5')

        self.pricelist = self.env.ref('product.list0')

    def test01_create_invoice_from_so(self):

        so = self.sale_object.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0,
                            {'name': self.products_ord.name,
                             'product_id': self.products_ord.id,
                             'product_uom_qty': 2,
                             'product_uom': self.products_ord.uom_id.id,
                             'price_unit': self.products_ord.list_price})],
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.pricelist.id,
        })

        so.action_confirm()
        inv_id = so.action_invoice_create()
        invoice = self.invoice_object.browse(inv_id)
        self.assertEqual(invoice.partner_id.id,
                         self.partner.id)

        self.assertEqual(invoice.address_shipping_id.id,
                         self.partner.id)

    def test02_create_invoice_from_stock(self):

        so = self.sale_object.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0,
                            {'name': self.products_del.name,
                             'product_id': self.products_del.id,
                             'product_uom_qty': 2,
                             'product_uom': self.products_del.uom_id.id,
                             'price_unit': self.products_del.list_price})],
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.pricelist.id,
        })

        so.action_confirm()

        sp_out = so.picking_ids
        wiz_act = sp_out.do_new_transfer()
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.process()

        inv_id = so.action_invoice_create()
        invoice = self.invoice_object.browse(inv_id)
        self.assertEqual(invoice.partner_id.id,
                         self.partner.id)

        self.assertEqual(invoice.address_shipping_id.id,
                         self.partner.id)
