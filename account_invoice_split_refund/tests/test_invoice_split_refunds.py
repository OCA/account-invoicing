# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install")
class TestInvoiceSplitRefunds(TestSaleCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        receivable_acc = cls.company_data["default_account_receivable"]
        customer = cls.env["res.partner"].create(
            {
                "name": "Customer",
                "email": "customer@example.com",
                "property_account_receivable_id": receivable_acc.id,
            }
        )

        cls.delivery_product = cls.env.ref("product.product_delivery_01")

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "name": cls.delivery_product.name,
                "product_id": cls.delivery_product.id,
                "product_uom_qty": 5,
                "product_uom": cls.delivery_product.uom_id.id,
                "price_unit": cls.delivery_product.list_price,
            }
        )
        cls.sale_order.action_confirm()

        cls.delivery_picking = cls.sale_order.picking_ids
        cls.delivery_picking.action_assign()
        cls.delivery_picking.move_ids.write({"quantity_done": 5})
        cls.delivery_picking.button_validate()

    def _create_backorder(self, picking, quantity):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.write({"quantity": quantity})
        action = stock_return_picking.create_returns()
        return_pick = self.env["stock.picking"].browse(action["res_id"])
        return_pick.move_ids.write({"quantity_done": quantity})
        return_pick._action_done()
        return return_pick

    def test_account_invoice_split_refund_and_invoice(self):
        self.invoice = self.sale_order._create_invoices()
        self.invoice.action_post()
        self._create_backorder(self.delivery_picking, 2)
        self.assertEqual(self.sale_order_line.qty_delivered, 3)
        self.assertEqual(self.sale_order_line.qty_invoiced, 5)

        service_product = self.env.ref("product.product_product_1")

        sale_order_line_2 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": service_product.name,
                "product_id": service_product.id,
                "product_uom_qty": 6,
                "qty_delivered": 6,
                "product_uom": service_product.uom_id.id,
                "price_unit": service_product.list_price,
            }
        )
        self.assertEqual(sale_order_line_2.qty_invoiced, 0)
        self.assertEqual(sale_order_line_2.qty_to_invoice, 6)
        create_invoice_wiz = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=self.sale_order.ids, active_id=self.sale_order.id)
            .create({})
        )
        self.assertEqual(create_invoice_wiz.advance_payment_method, "all_split")
        create_invoice_wiz.create_invoices()
        self.assertEqual(len(self.sale_order.invoice_ids), 3)

        new_refund = self.sale_order.invoice_ids.filtered(
            lambda i: i.move_type == "out_refund"
        )
        new_invoice = self.sale_order.invoice_ids - new_refund - self.invoice

        self.assertEqual(new_refund.invoice_line_ids.product_id, self.delivery_product)
        # As we invoiced 5 and returned 2, we must refund 2
        self.assertEqual(new_refund.invoice_line_ids.quantity, 2)
        self.assertEqual(new_invoice.invoice_line_ids.product_id, service_product)

        self.assertEqual(new_invoice.invoice_line_ids.quantity, 6)

    def test_invoice_split_invoice(self):
        create_invoice_wiz = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=self.sale_order.ids, active_id=self.sale_order.id)
            .create({})
        )
        create_invoice_wiz.create_invoices()
        self.assertEqual(len(self.sale_order.invoice_ids), 1)

    def test_invoice_split_refund(self):
        self.invoice = self.sale_order._create_invoices()
        self.invoice.action_post()
        self._create_backorder(self.delivery_picking, 2)
        self.assertEqual(self.sale_order_line.qty_to_invoice, -2)
        create_invoice_wiz = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=self.sale_order.ids, active_id=self.sale_order.id)
            .create({})
        )
        create_invoice_wiz.create_invoices()
        new_refund = self.sale_order.invoice_ids.filtered(
            lambda i: i.move_type == "out_refund"
        )
        self.assertEqual(new_refund.invoice_line_ids.quantity, 2)
