# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.sale_order_whole_delivered_invoiceability.tests import (
    test_sale_order_whole_delivered_invoiceability,
)


class TestSaleOrderTypeWholeDeliveredInvoiceability(
    test_sale_order_whole_delivered_invoiceability.TestSaleOrderWholeDeliveredInvoiceability
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_type = cls.env["sale.order.type"].create(
            [
                {
                    "name": "Test Normal Order",
                    "whole_delivered_invoiceability": True,
                },
            ]
        )

    def test_whole_delivered_invoiceability_type(self):
        self.partner.whole_delivered_invoiceability = False
        self.order.whole_delivered_invoiceability = False
        with Form(self.order) as order_form:
            order_form.type_id = self.sale_order_type
        self.assertTrue(self.order.whole_delivered_invoiceability)
