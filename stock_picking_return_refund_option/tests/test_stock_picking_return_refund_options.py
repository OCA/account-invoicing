# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderLineInput(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test", "customer_rank": 1, "supplier_rank": 1}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "product", "invoice_policy": "delivery"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "test_product_2", "type": "product", "invoice_policy": "delivery"}
        )
        with Form(cls.env["sale.order"]) as order_form:
            order_form.partner_id = cls.partner
            with order_form.order_line.new() as line_form:
                line_form.product_id = cls.product
                line_form.product_uom_qty = 1
            with order_form.order_line.new() as line_form:
                line_form.product_id = cls.product2
                line_form.product_uom_qty = 1
        cls.order = order_form.save()
        cls.order.action_confirm()
        cls.picking = cls.order.picking_ids
        move_line_vals_list = []
        for move in cls.picking.move_lines:
            move_line_vals = move._prepare_move_line_vals()
            move_line_vals["qty_done"] = 1
            move_line_vals_list.append(move_line_vals)
        cls.env["stock.move.line"].create(move_line_vals_list)
        cls.picking.action_done()
        cls.order._create_invoices()

    def get_return_picking_wizard(self, picking):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return stock_return_picking_form.save()

    def return_picking_wiz(self, picking):
        wizard = self.get_return_picking_wizard(picking)
        wizard.product_return_moves.write({"quantity": 1.0, "to_refund": False})
        return wizard

    def test_return_to_refund_values(self):
        return_wizard = self.return_picking_wiz(self.picking)
        return_pick = self.picking.browse(return_wizard.create_returns()["res_id"])
        return_pick.move_line_ids.write({"qty_done": 1.0})
        return_pick.action_done()
        self.assertEqual(return_pick.to_refund_lines, "no_refund")
        return_pick.move_lines.write({"to_refund": True})
        self.assertEqual(return_pick.to_refund_lines, "to_refund")
        return_pick.move_lines[:1].write({"to_refund": False})
        self.assertFalse(return_pick.to_refund_lines)

    def test_return_so_wo_to_refund(self):
        # Return some items, after SO was invoiced
        return_wizard = self.return_picking_wiz(self.picking)
        return_pick = self.picking.browse(return_wizard.create_returns()["res_id"])
        return_pick.move_line_ids.write({"qty_done": 1.0})
        return_pick.action_done()
        self.assertEqual(self.order.invoice_status, "invoiced")

        return_pick.to_refund_lines = "to_refund"
        self.assertEqual(self.order.invoice_status, "to invoice")

        return_pick.to_refund_lines = "no_refund"
        self.assertEqual(self.order.invoice_status, "invoiced")

        return_pick.to_refund_lines = False
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.assertTrue(return_pick.is_return)
        self.assertFalse(self.picking.is_return)

    def test_return_po_wo_to_refund(self):
        if not self.env.registry.models.get("purchase.order", False):
            return True
        po_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 1000.00,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        po_order.button_confirm()
        picking = po_order.picking_ids[:]
        picking.move_line_ids.write({"qty_done": 1.0})
        picking.action_done()
        self.assertEqual(po_order.invoice_status, "to invoice")
        # Return the picking without refund
        return_wizard = self.return_picking_wiz(picking)
        return_pick = self.picking.browse(return_wizard.create_returns()["res_id"])
        move_line_vals = return_pick.move_lines._prepare_move_line_vals()
        move_line_vals["qty_done"] = 1
        self.env["stock.move.line"].create(move_line_vals)
        return_pick.action_done()
        # Now set to be refunded
        return_pick.to_refund_lines = "to_refund"
        self.assertEqual(po_order.invoice_status, "no")
        # And again to not be refunded
        return_pick.to_refund_lines = "no_refund"
        self.assertEqual(po_order.invoice_status, "to invoice")
