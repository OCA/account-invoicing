# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import Form

from .common import TestAccountInvoiceSectionPickingCommon


class TestAccountInvoiceSectionPicking(TestAccountInvoiceSectionPickingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.invoice_section_grouping = "delivery_picking"
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_delivery_01")
        stock = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"]._update_available_quantity(cls.product_1, stock, 1000)
        cls.product_1.invoice_policy = "order"
        cls.order_1 = cls._create_order()
        cls.order_2 = cls._create_order(order_line_name=cls.product_1.name)

    @classmethod
    def _create_order(cls, order_line_name=None):
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner_1
        with order_form:
            with order_form.order_line.new() as line_form:
                line_form.product_id = cls.product_1
                line_form.product_uom_qty = 5
                if order_line_name is not None:
                    line_form.name = order_line_name
        return order_form.save()

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
