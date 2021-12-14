# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from .common import TestAccountInvoiceSectionPickingCommon


class TestAccountInvoiceSectionPicking(TestAccountInvoiceSectionPickingCommon):
    def test_group_by_delivery_picking(self):
        self.order_1.action_confirm()
        self.order_2.action_confirm()

        invoice = (self.order_1 + self.order_2)._create_invoices()
        self.assertEqual(len(invoice), 1)
        result = {
            10: (self.order_1.picking_ids.name, "line_section"),
            20: (self.order_1.order_line.name, False),
            30: (self.order_2.picking_ids.name, "line_section"),
            40: (self.order_2.order_line.name, False),
        }
        for line in invoice.invoice_line_ids.sorted("sequence"):
            self.assertEqual(line.name, result[line.sequence][0])
            self.assertEqual(line.display_type, result[line.sequence][1])

    def test_group_by_delivery_picking_multi_steps(self):
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.write({"delivery_steps": "pick_pack_ship"})

        self.order_1.action_confirm()
        self.order_2.action_confirm()

        invoice = (self.order_1 + self.order_2)._create_invoices()
        self.assertEqual(len(invoice), 1)
        result = {
            10: (self.order_1.order_line.move_ids.picking_id.name, "line_section"),
            20: (self.order_1.order_line.name, False),
            30: (self.order_2.order_line.move_ids.picking_id.name, "line_section"),
            40: (self.order_2.order_line.name, False),
        }
        for line in invoice.invoice_line_ids.sorted("sequence"):
            self.assertEqual(line.name, result[line.sequence][0])
            self.assertEqual(line.display_type, result[line.sequence][1])

    def test_group_by_delivery_picking_backorder(self):
        self.order_1.action_confirm()
        self.order_2.action_confirm()

        delivery_1_move = self.order_1.order_line.move_ids
        delivery_1_move.move_line_ids.qty_done = 2.0
        delivery_1 = delivery_1_move.picking_id
        backorder_wiz_action = delivery_1.button_validate()
        backorder_wiz = (
            self.env["stock.backorder.confirmation"]
            .with_context(**backorder_wiz_action.get("context"))
            .create({})
        )
        backorder_wiz.process()
        delivery_1_backorder_move = self.order_1.order_line.move_ids - delivery_1_move
        delivery_1_backorder = delivery_1_backorder_move.picking_id
        delivery_2 = self.order_2.order_line.move_ids.picking_id
        invoice = (self.order_1 + self.order_2)._create_invoices()
        result = {
            10: (
                ", ".join([delivery_1.name, delivery_1_backorder.name]),
                "line_section",
            ),
            20: (self.order_1.order_line.name, False),
            30: (delivery_2.name, "line_section"),
            40: (self.order_2.order_line.name, False),
        }
        for line in invoice.invoice_line_ids.sorted("sequence"):
            self.assertEqual(line.name, result[line.sequence][0])
            self.assertEqual(line.display_type, result[line.sequence][1])
