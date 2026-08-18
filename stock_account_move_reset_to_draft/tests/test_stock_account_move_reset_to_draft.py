# Copyright 2024 Tecnativa - Víctor Martínez
# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TestStockAccountMoveResetToDraft(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.env.company.chart_template_id:
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)
        cls.category = cls.env["product.category"].create(
            {
                "name": "Test product",
                "property_cost_method": "average",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "categ_id": cls.category.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.group = cls.env.ref(
            "stock_account_move_reset_to_draft.group_stock_move_force_reset_to_draft"
        )

    def create_and_confirm_order(self, price=10, qty=1):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = qty
            line_form.price_unit = price
            line_form.taxes_id.clear()
        order = order_form.save()
        order.button_confirm()
        return order

    def process_picking(self, picking, qty_done=None):
        if qty_done is not None:
            picking.move_ids_without_package.quantity_done = qty_done
        res = picking.button_validate()
        wizard = self.env[res["res_model"]].with_context(**res["context"]).create({})
        wizard.process()
        self.assertEqual(picking.state, "done")

    def create_and_post_invoice(self, order, price=10, qty=1):
        res_invoice = order.action_create_invoice()
        invoice = self.env[res_invoice["res_model"]].browse(res_invoice["res_id"])
        self.assertEqual(invoice.state, "draft")
        invoice.invoice_date = order.date_approve
        invoice.invoice_line_ids.write({"quantity": qty, "price_unit": price})
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        return invoice

    @mute_logger("odoo.models.unlink")
    def test_purchase_order_flow_01(self):
        order = self.create_and_confirm_order(price=10, qty=1)
        self.process_picking(order.picking_ids)
        invoice = self.create_and_post_invoice(order, price=12, qty=1)
        # Upon confirmation, a SVL will be created for the difference (2=12-10)
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 1)
        svl_1 = invoice.invoice_line_ids.stock_valuation_layer_ids
        self.assertEqual(svl_1.value, 2)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 2
        )
        self.assertTrue(invoice.show_reset_to_draft_button)
        # Switch to draft, a SVL will be created for the difference
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 2)
        self.assertEqual(svl_1.value, 2)
        svl_1_negative = invoice.invoice_line_ids.stock_valuation_layer_ids - svl_1
        self.assertEqual(svl_1_negative.value, -2)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 0
        )
        # Confirm again, no new SVLs are generated
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 2)
        self.assertEqual(svl_1.value, 2)
        self.assertEqual(svl_1_negative.value, -2)
        self.assertTrue(invoice.show_reset_to_draft_button)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 0
        )
        # Change to draft and change the price to 10 so that SVL is not generated
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 2)
        self.assertEqual(svl_1.value, 2)
        self.assertEqual(svl_1_negative.value, -2)
        invoice.invoice_line_ids.price_unit = 10
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 2)
        self.assertEqual(svl_1.value, 2)
        self.assertEqual(svl_1_negative.value, -2)
        self.assertTrue(invoice.show_reset_to_draft_button)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 0
        )

    @mute_logger("odoo.models.unlink")
    def test_purchase_order_flow_02(self):
        # PO for a product: 2 pcs at EUR10
        order = self.create_and_confirm_order(price=10, qty=2)
        # Receive 1 pc and create a backorder
        picking = order.picking_ids
        self.process_picking(picking, qty_done=1)
        extra_picking = order.picking_ids - picking
        self.process_picking(extra_picking)
        invoice = self.create_and_post_invoice(order, price=12, qty=2)
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 2)
        svls_1 = invoice.invoice_line_ids.stock_valuation_layer_ids
        self.assertEqual(sum(svls_1.mapped("value")), 4)
        self.assertTrue(invoice.show_reset_to_draft_button)
        # Reset the bill to draft
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 4)
        svls_1_negative = invoice.invoice_line_ids.stock_valuation_layer_ids - svls_1
        self.assertEqual(sum(svls_1.mapped("value")), 4)
        self.assertEqual(sum(svls_1_negative.mapped("value")), -4)
        # Change the bill content to 1 pc at EUR15 and post
        invoice.invoice_line_ids.write({"quantity": 1, "price_unit": 15})
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 4)
        # Create another bill for 1 pc at EUR8 and post
        invoice_extra = self.create_and_post_invoice(order, price=8, qty=1)
        self.assertEqual(
            len(invoice_extra.invoice_line_ids.stock_valuation_layer_ids), 1
        )
        self.assertEqual(
            invoice_extra.invoice_line_ids.stock_valuation_layer_ids.value, -2
        )
        self.assertTrue(invoice.show_reset_to_draft_button)
        # Reset the first bill to draft -> User error to prevent valuation inconsistencies
        with self.assertRaises(UserError):
            invoice.button_draft()

    @mute_logger("odoo.models.unlink")
    def test_purchase_order_flow_03(self):
        order = self.create_and_confirm_order(price=10, qty=1)
        self.process_picking(order.picking_ids)
        invoice = self.create_and_post_invoice(order, price=12, qty=1)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 2
        )
        # Manually create an SVL linked to the original SVL.
        # This simulates cases such as applying a landed cost to a receipt.
        svl = order.picking_ids.move_ids.stock_valuation_layer_ids
        self.env["stock.valuation.layer"].create(
            {
                "product_id": self.product.id,
                "value": 5,
                "quantity": 1,
                "description": "Manual SVL",
                "stock_move_id": False,
                "stock_valuation_layer_id": svl.id,
                "company_id": self.env.company.id,
            }
        )
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 0
        )

    @mute_logger("odoo.models.unlink")
    def test_purchase_order_flow_wizard(self):
        self.env.user.groups_id |= self.group
        order = self.create_and_confirm_order(price=10, qty=1)
        self.process_picking(order.picking_ids)
        invoice = self.create_and_post_invoice(order, price=12, qty=1)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 2
        )
        # Create an outgoing move
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "location_id": order.picking_ids.location_dest_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_uom_qty": 1.0,
            }
        )
        move._action_confirm()
        move._action_assign()
        self.assertEqual(
            "assigned",
            move.state,
        )
        move.move_line_ids.qty_done = 1.0
        move._action_done()

        result = invoice.button_draft()
        wizard_model = "stock.account.move.reset.to.draft"
        self.assertEqual(wizard_model, result.get("res_model"))
        context = result.get("context")
        wizard = self.env[wizard_model].with_context(**context).create({})

        wizard.doit()

        # Valuations haven't changed
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 2.0
        )

        # Revalidate invoice
        invoice._post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 2.0
        )
        self.assertFalse(invoice.dont_regenerate_valuation)

    @mute_logger("odoo.models.unlink")
    def test_purchase_order_consume_error(self):
        order = self.create_and_confirm_order(price=10, qty=1)
        self.process_picking(order.picking_ids)
        invoice = self.create_and_post_invoice(order, price=12, qty=1)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 2
        )
        # Create an outgoing move
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "location_id": order.picking_ids.location_dest_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_uom_qty": 1.0,
            }
        )
        move._action_confirm()
        move._action_assign()
        self.assertEqual(
            "assigned",
            move.state,
        )
        move.move_line_ids.qty_done = 1.0
        move._action_done()

        with self.assertRaises(UserError) as error:
            invoice.button_draft()
        invoice_name = invoice.invoice_line_ids.display_name
        self.assertEqual(
            error.exception.args[0],
            f"The inventory has already been (partially) consumed for {invoice_name}.",
        )

    @mute_logger("odoo.models.unlink")
    def test_purchase_order_flow_wizard_intertwined(self):
        self.env.user.groups_id |= self.group
        # PO for a product: 2 pcs at EUR10
        order = self.create_and_confirm_order(price=10, qty=2)
        # Receive 1 pc and create a backorder
        picking = order.picking_ids
        self.process_picking(picking, qty_done=1)
        extra_picking = order.picking_ids - picking
        self.process_picking(extra_picking)
        invoice = self.create_and_post_invoice(order, price=12, qty=2)
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 2)
        svls_1 = invoice.invoice_line_ids.stock_valuation_layer_ids
        self.assertEqual(sum(svls_1.mapped("value")), 4)
        self.assertTrue(invoice.show_reset_to_draft_button)
        # Reset the bill to draft
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")
        # We should have done nothing
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 4)
        svls_1_negative = invoice.invoice_line_ids.stock_valuation_layer_ids - svls_1
        self.assertEqual(sum(svls_1.mapped("value")), 4)
        self.assertEqual(sum(svls_1_negative.mapped("value")), -4)
        # Change the bill content to 1 pc at EUR15 and post
        invoice.invoice_line_ids.write({"quantity": 1, "price_unit": 15})
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(len(invoice.invoice_line_ids.stock_valuation_layer_ids), 4)
        # Create another bill for 1 pc at EUR8 and post
        invoice_extra = self.create_and_post_invoice(order, price=8, qty=1)
        self.assertEqual(
            len(invoice_extra.invoice_line_ids.stock_valuation_layer_ids), 1
        )
        self.assertEqual(
            invoice_extra.invoice_line_ids.stock_valuation_layer_ids.value, -2
        )
        self.assertTrue(invoice.show_reset_to_draft_button)
        # Reset the first bill to draft -> User error to prevent valuation inconsistencies
        result = invoice.button_draft()
        wizard_model = "stock.account.move.reset.to.draft"
        self.assertEqual(wizard_model, result.get("res_model"))
        context = result.get("context")
        wizard = self.env[wizard_model].with_context(**context).create({})

        self.assertTrue(wizard.intertwined_move_line_ids)

        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 0.0
        )

        wizard.doit()

        # Valuations haven't changed
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 0.0
        )

        # Revalidate invoice
        invoice._post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped("stock_valuation_layer_ids.value")), 0.0
        )
