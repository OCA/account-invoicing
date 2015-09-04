# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestInvoiceProductGroup(TransactionCase):

    def transfer_picking(self, picking):
        picking.invoice_state = '2binvoiced'
        picking.action_confirm()
        picking.force_assign()
        picking.do_prepare_partial()
        picking.do_transfer()

    def setUp(self):
        super(TestInvoiceProductGroup, self).setUp()
        self.invoice_model = self.env['account.invoice']
        self.picking_model = self.env['stock.picking']
        self.move_model = self.env['stock.move']
        self.onshipping_model = self.env['stock.invoice.onshipping']
        # ---------------------------------------------------------------------
        # Get demo data
        # ---------------------------------------------------------------------
        self.partner_1 = self.env.ref(
            'stock_picking_invoice_product_group.partner_1')
        self.partner_2 = self.env.ref(
            'stock_picking_invoice_product_group.partner_2')
        product_A = self.env.ref(
            'stock_picking_invoice_product_group.product_A')
        product_B = self.env.ref(
            'stock_picking_invoice_product_group.product_B')
        product_C = self.env.ref(
            'stock_picking_invoice_product_group.product_C')
        product_D = self.env.ref(
            'stock_picking_invoice_product_group.product_D')
        # ---------------------------------------------------------------------
        # Create delivery orders of product A, B, C, D
        # ---------------------------------------------------------------------
        picking_1 = self.picking_model.create({
            'partner_id': self.partner_1.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id})
        self.move_model.create({
            'name': '/',
            'picking_id': picking_1.id,
            'product_uom_qty': 2.0,
            'product_id':  product_A.id,
            'product_uom': product_A.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        self.move_model.create({
            'name': '/',
            'picking_id': picking_1.id,
            'product_uom_qty': 2.0,
            'product_id': product_B.id,
            'product_uom': product_B.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        picking_2 = self.picking_model.create({
            'partner_id': self.partner_2.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id})
        self.move_model.create({
            'name': '/',
            'picking_id': picking_2.id,
            'product_uom_qty': 2.0,
            'product_id': product_C.id,
            'product_uom': product_C.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        self.move_model.create({
            'name': '/',
            'picking_id': picking_2.id,
            'product_uom_qty': 2.0,
            'product_id': product_D.id,
            'product_uom': product_D.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        picking_3 = self.picking_model.create({
            'partner_id': self.partner_1.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id})
        self.move_model.create({
            'name': '/',
            'picking_id': picking_3.id,
            'product_uom_qty': 2.0,
            'product_id': product_C.id,
            'product_uom': product_C.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        self.move_model.create({
            'name': '/',
            'picking_id': picking_3.id,
            'product_uom_qty': 2.0,
            'product_id': product_D.id,
            'product_uom': product_D.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        self.move_model.create({
            'name': '/',
            'picking_id': picking_3.id,
            'product_uom_qty': 2.0,
            'product_id': product_A.id,
            'product_uom': product_A.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        # ---------------------------------------------------------------------
        # Transfer delivery orders
        # ---------------------------------------------------------------------
        self.transfer_picking(picking_1)
        self.transfer_picking(picking_2)
        self.transfer_picking(picking_3)
        self.picking_ids = [picking_1.id, picking_2.id, picking_3.id]

    def test_group_by_default(self):
        wizard = self.onshipping_model.with_context(
            {'active_ids': self.picking_ids}).create({'group': False})
        invoice_ids = wizard.create_invoice()
        invoices = self.env['account.invoice'].browse(invoice_ids)
        self.assertEqual(3, len(invoices))
        for invoice in invoices:
            self.assertEqual(invoice.type, 'out_invoice')
        invoices_1 = self.invoice_model.search(
            [('partner_id', '=', self.partner_1.id)])
        self.assertEqual(2, len(invoices_1))
        invoices_2 = self.invoice_model.search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEqual(1, len(invoices_2))

    def test_group_by_partner(self):
        wizard = self.onshipping_model.with_context(
            {'active_ids': self.picking_ids}).create({'group': True})
        invoice_ids = wizard.create_invoice()
        invoices = self.env['account.invoice'].browse(invoice_ids)
        self.assertEqual(2, len(invoices))
        for invoice in invoices:
            self.assertEqual(invoice.type, 'out_invoice')
        invoices_1 = self.invoice_model.search(
            [('partner_id', '=', self.partner_1.id)])
        self.assertEqual(1, len(invoices_1))
        invoices_2 = self.invoice_model.search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEqual(1, len(invoices_2))

    def test_group_by_category(self):
        wizard = self.onshipping_model.with_context(
            {'active_ids': self.picking_ids}).create(
                {'group_type': 'group_by_product_category'})
        invoice_ids = wizard.create_invoice()
        invoices = self.env['account.invoice'].browse(invoice_ids)
        self.assertEqual(5, len(invoices))
        for invoice in invoices:
            self.assertEqual(invoice.type, 'out_invoice')
            # check if each invoice contains product of the same category
            categories = invoice.mapped('invoice_line.product_id.categ_id')
            self.assertEqual(1, len(categories))
        invoices_1 = self.invoice_model.search(
            [('partner_id', '=', self.partner_1.id)])
        self.assertEqual(3, len(invoices_1))
        invoices_2 = self.invoice_model.search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEqual(2, len(invoices_2))

    def test_group_by_product(self):
        wizard = self.onshipping_model.with_context(
            {'active_ids': self.picking_ids}).create(
                {'group_type': 'group_by_product'})
        invoice_ids = wizard.create_invoice()
        invoices = self.env['account.invoice'].browse(invoice_ids)
        self.assertEqual(6, len(invoices))
        for invoice in invoices:
            self.assertEqual(invoice.type, 'out_invoice')
            # check if each invoice contains same product
            products = invoice.mapped('invoice_line.product_id')
            self.assertEqual(1, len(products))
        invoices_1 = self.invoice_model.search(
            [('partner_id', '=', self.partner_1.id)])
        self.assertEqual(4, len(invoices_1))
        invoices_2 = self.invoice_model.search(
            [('partner_id', '=', self.partner_2.id)])
        self.assertEqual(2, len(invoices_2))
