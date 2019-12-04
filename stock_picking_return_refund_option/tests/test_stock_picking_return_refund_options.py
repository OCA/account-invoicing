# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase, tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestSaleOrderLineInput(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test',
            'sale_discount': 10.0,
            'customer': True,
            'supplier': True,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'test_product',
            'type': 'product',
            'invoice_policy': 'delivery',
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'test_product_2',
            'type': 'product',
            'invoice_policy': 'delivery',
        })
        cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'quantity': 12.0,
        })
        cls.env['stock.quant'].create({
            'product_id': cls.product2.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'quantity': 12.0,
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 1000.00,
            }), (0, 0, {
                'name': cls.product2.name,
                'product_id': cls.product2.id,
                'product_uom_qty': 1,
                'product_uom': cls.product2.uom_id.id,
                'price_unit': 1000.00,
            })],
            'pricelist_id': cls.env.ref('product.list0').id,
        })
        cls.order.action_confirm()
        cls.picking = cls.order.picking_ids
        cls.picking.move_line_ids.write({'qty_done': 1.0})
        cls.picking.action_done()
        cls.order.action_invoice_create()

    def return_picking_wiz(self, picking):
        wizard = self.env["stock.return.picking"].with_context(
            active_id=picking.id).create({})
        wizard.product_return_moves.write({
            "quantity": 1.0,
            "to_refund": False,
        })
        return wizard

    def test_return_to_refund_values(self):
        return_wizard = self.return_picking_wiz(self.picking)
        return_pick = self.picking.browse(
            return_wizard.create_returns()["res_id"])
        return_pick.move_line_ids.write({'qty_done': 1.0})
        return_pick.action_done()
        self.assertEqual(return_pick.to_refund_lines, 'no_refund')
        return_pick.move_lines.write({'to_refund': True})
        self.assertEqual(return_pick.to_refund_lines, 'to_refund')
        return_pick.move_lines[:1].write({'to_refund': False})
        self.assertFalse(return_pick.to_refund_lines)

    def test_return_so_wo_to_refund(self):
        # Return some items, after SO was invoiced
        return_wizard = self.return_picking_wiz(self.picking)
        return_pick = self.picking.browse(
            return_wizard.create_returns()["res_id"])
        return_pick.move_line_ids.write({'qty_done': 1.0})
        return_pick.action_done()
        self.assertEqual(self.order.invoice_status, 'invoiced')

        return_pick.to_refund_lines = 'to_refund'
        self.assertEqual(self.order.invoice_status, 'to invoice')

        return_pick.to_refund_lines = 'no_refund'
        self.assertEqual(self.order.invoice_status, 'invoiced')

        return_pick.to_refund_lines = False
        self.assertEqual(self.order.invoice_status, 'invoiced')
        self.assertTrue(return_pick.is_return)
        self.assertFalse(self.picking.is_return)

    def test_return_po_wo_to_refund(self):
        if not self.env.registry.models.get('purchase.order', False):
            return True
        po_order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_qty': 1.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': 1000.00,
                'date_planned': fields.Datetime.now(),
            })],
        })
        po_order.button_confirm()
        picking = po_order.picking_ids[:]
        picking.move_line_ids.write({'qty_done': 1.0})
        picking.action_done()
        self.assertEqual(po_order.invoice_status, 'to invoice')

        return_wizard = self.return_picking_wiz(picking)
        return_pick = self.picking.browse(
            return_wizard.create_returns()["res_id"])
        return_pick.move_line_ids.write({'qty_done': 1.0})
        return_pick.action_done()

        return_pick.to_refund_lines = 'to_refund'
        self.assertEqual(po_order.invoice_status, 'no')

        return_pick.to_refund_lines = 'no_refund'
        self.assertEqual(po_order.invoice_status, 'to invoice')
