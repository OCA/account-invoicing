# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import Form, SavepointCase


class TestAccountInvoiceSectionPickingCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
