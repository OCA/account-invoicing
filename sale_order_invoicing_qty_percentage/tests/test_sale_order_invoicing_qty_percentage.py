# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderInvoicingQtyPercentage(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
                "invoice_policy": "order",
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 20,
                        }
                    )
                ],
            }
        )
        cls.order.action_confirm()
        cls.wizard = (
            cls.env["sale.advance.payment.inv"]
            .with_context(
                active_id=cls.order.id,
                active_ids=cls.order.ids,
                active_model="sale.order",
            )
            .create({"advance_payment_method": "qty_percentage", "qty_percentage": 50})
        )

    def test_invoicing_same_data(self):
        self.wizard.create_invoices()
        self.assertEqual(self.order.invoice_ids.invoice_line_ids.quantity, 10)
        self.assertEqual(self.order.order_line.qty_to_invoice, 10)
