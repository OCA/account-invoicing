# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp.tests.common import TransactionCase
import datetime


class TestStockPickingInvoice(TransactionCase):

    def setUp(self):
        super(TestStockPickingInvoice, self).setUp()
        self.stock_picking = self.env['stock.picking']
        self.stock_move = self.env['stock.move']
        self.date_today = datetime.datetime.now()
        self.picking_type_id = self.env.ref('stock.picking_type_in')
        self.stock_location = self.env.ref('stock.location_inventory')
        self. customer_location =\
            self.env.ref('stock.stock_location_customers')
        self.bank = self.env['res.partner.bank'].create({
            'state': 'bank',
            'acc_number': 12345678901234,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'customer': True,
            'default_company_bank_id': self.bank.id
        })
        self.uom_unit = self.env.ref('product.product_uom_unit')
        product = self.env['product.product']
        self.product_test = product.create({
            'name': 'Test Product',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'lst_price': 11.55})

        self.create_picking()

    def create_picking(self):
        self.picking = self.stock_picking.create({
            'partner_id': self.partner.id,
            'date': self.date_today,
            'min_date': self.date_today,
            'picking_type_id': self.picking_type_id.id,
        })
        self.move = self.stock_move.create({
            'name': 'Test move',
            'product_id': self.product_test.id,
            'product_uom_qty': 3.0,
            'product_uom': self.uom_unit.id,
            'picking_id': self.picking.id,
            'invoice_state': '2binvoiced',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id
        })
        self.picking.action_confirm()
        self.picking.do_enter_transfer_details()
        wiz_detail_obj = self.env['stock.transfer_details']
        wiz_detail = wiz_detail_obj.with_context(
            active_model='stock.picking',
            active_ids=[self.picking.id],
            active_id=self.picking.id).create({'picking_id': self.picking.id})
        wiz_detail.item_ids[0].quantity = 2
        wiz_detail.do_detailed_transfer()

        self.onshipping_Wizard = self.env['stock.invoice.onshipping']
        self.wizard = self.onshipping_Wizard.with_context({
            'active_id': self.picking.id,
            'active_ids': self.picking.ids,
        }).create({})
        self.wizard.open_invoice()

    def test_account_invoice_from_picking(self):
        invoice = self.env['account.invoice'].search([
            ('origin', '=', self.picking.name)
        ])
        self.assertEqual(self.partner.default_company_bank_id.acc_number,
                         invoice.partner_bank_id.acc_number)
