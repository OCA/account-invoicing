from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install", "standart")
class TestSaleOrder(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestSaleOrder, self).setUp(*args, **kwargs)

        self.partner1 = self.env["res.partner"].create({"name": "Test"})
        self.product1 = self.env["product.product"].create({"name": "desktop"})
        self.product2 = self.env["product.product"].create({"name": "table"})

        self.sale_order_1 = self.env["sale.order"].create(
            {"partner_id": self.partner1.id}
        )
        self.env["ir.config_parameter"].sudo().set_param("so.no_autofollow", True)

    def test_in_sale_order_create(self):
        with Form(self.sale_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product1
            form.save()
        sale_order = self.sale_order_1
        self.assertNotIn(
            sale_order.partner_id.id,
            sale_order.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_in_sale_order_write(self):
        with Form(self.sale_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product1
            with form.order_line.new() as line_1:
                line_1.product_id = self.product2
            form.save()
        sale_order = self.sale_order_1
        self.assertNotIn(
            sale_order.partner_id.id,
            sale_order.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_in_sale_order_action_confirm(self):
        with Form(self.sale_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product1
            form.save()
        sale_order = self.sale_order_1
        sale_order.action_confirm()
        self.assertNotIn(
            sale_order.partner_id.id,
            sale_order.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_in_sale_order_action_quotation_send(self):
        with Form(self.sale_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product1
            form.save()
        sale_order = self.sale_order_1
        sale_order.action_quotation_send()
        self.assertNotIn(
            sale_order.partner_id.id,
            sale_order.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )
