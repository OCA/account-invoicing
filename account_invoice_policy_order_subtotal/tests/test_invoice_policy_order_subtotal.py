# Copyright 2022 Camptocamp SA <telmo.santos@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase


class TestInvoicePolicyOrderSubtotal(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.SaleOrder = cls.env["sale.order"]
        cls.Product = cls.env["product.product"]
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product1 = cls.env.ref("product.product_delivery_01")
        cls.product2 = cls.Product.create(
            {
                "name": "Product Invoice policy order subtotal",
                "categ_id": cls.env.ref("product.product_category_consumable").id,
                "type": "consu",
                "default_code": "prod_inv_pol_order_subtotal",
                "invoice_policy": "order_subtotal",
            }
        )

        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Line 1",
                            "product_id": cls.product1.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.product1.uom_id.id,
                            "price_unit": 500,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Product Invoice policy order subtotal positive",
                            "product_id": cls.product2.id,
                            "product_uom_qty": 0.02,
                            "product_uom": cls.product2.uom_id.id,
                            "price_unit": 2000,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Product Invoice policy order subtotal negative",
                            "product_id": cls.product2.id,
                            "product_uom_qty": 0.02,
                            "product_uom": cls.product2.uom_id.id,
                            "price_unit": -2000,
                        },
                    ),
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

    def _get_sale_advance_payment_inv_wizard(self):
        return (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=self.so1.ids)
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )

    def test_sale_order_lines_invoiced_amount(self):
        self.so1.action_confirm()
        self.so1.order_line[0].qty_delivered = 2
        wiz = self._get_sale_advance_payment_inv_wizard()
        self.assertEqual(self.so1.order_line[0].invoice_status, "to invoice")
        self.assertEqual(self.so1.order_line[1].invoice_status, "to invoice")

        # 1st Invoice
        wiz.create_invoices()
        invoice1 = self.so1.invoice_ids
        self.assertEqual(self.so1.order_line[0].amount_invoiced, 1000.0)
        self.assertEqual(self.so1.order_line[1].amount_invoiced, 0.0)
        self.assertEqual(self.so1.order_line[0].invoice_status, "no")
        self.assertEqual(self.so1.order_line[1].invoice_status, "to invoice")

        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].quantity = 0.01
        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].price_unit = 2000.0
        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].quantity = 0.01
        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].price_unit = -2000.0
        self.assertEqual(self.so1.order_line[0].invoice_status, "no")
        self.assertEqual(self.so1.order_line[1].amount_invoiced, 20.0)
        self.assertEqual(self.so1.order_line[1].invoice_status, "to invoice")
        self.assertEqual(self.so1.order_line[2].amount_invoiced, -20.0)
        self.assertEqual(self.so1.order_line[2].invoice_status, "to invoice")

        invoice1.action_post()
        # 2nd Invoice - Refund 1st Invoice
        self.env["account.move.reversal"].with_context(
            active_ids=invoice1.ids, active_model="account.move"
        ).create(
            {"refund_method": "refund", "reason": "The refund reason"}
        ).reverse_moves()
        self.so1.invoice_ids[1].action_post()
        self.assertEqual(self.so1.order_line[0].amount_invoiced, 0)
        self.assertEqual(self.so1.order_line[1].amount_invoiced, 0)
        self.assertEqual(self.so1.order_line[2].amount_invoiced, 0)
        self.assertEqual(self.so1.order_line[0].invoice_status, "to invoice")
        self.assertEqual(self.so1.order_line[1].invoice_status, "to invoice")
        self.assertEqual(self.so1.order_line[2].invoice_status, "to invoice")

        # 3rd Invoice - Create again 1st Invoice
        wiz.create_invoices()
        invoice3 = self.so1.invoice_ids[2]
        invoice3.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].quantity = 0.01
        invoice3.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].price_unit = 2000.0
        invoice3.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].quantity = 0.01
        invoice3.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].price_unit = -2000.0
        invoice3.action_post()

        # 4th Invoice
        self.so1.order_line[0].qty_delivered = 4
        wiz.create_invoices()
        invoice4 = self.so1.invoice_ids[3]
        invoice4.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].quantity = 0.01
        invoice4.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].price_unit = 2000.0
        invoice4.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].quantity = 0.01
        invoice4.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].price_unit = -2000.0
        invoice4.action_post()
        self.assertEqual(self.so1.order_line[0].amount_invoiced, 2000.0)
        self.assertEqual(self.so1.order_line[1].amount_invoiced, 40.0)
        self.assertEqual(self.so1.order_line[2].amount_invoiced, -40.0)
        self.assertEqual(self.so1.order_line[0].invoice_status, "invoiced")
        self.assertEqual(self.so1.order_line[1].invoice_status, "invoiced")
        self.assertEqual(self.so1.order_line[2].invoice_status, "invoiced")
        self.assertEqual(self.so1.invoice_status, "invoiced")

    def test_sale_order_invoiceable_lines(self):
        self.so1.action_confirm()
        self.so1.order_line[0].qty_delivered = 4
        wiz = self._get_sale_advance_payment_inv_wizard()
        wiz.create_invoices()
        invoice1 = self.so1.invoice_ids
        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].quantity = 0.01
        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].price_unit = 2000.0
        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].quantity = 0.01
        invoice1.with_context(check_move_validity=False).invoice_line_ids[
            2
        ].price_unit = -2000.0

        lines = self.so1._get_invoiceable_lines()
        self.assertEqual(len(lines), 2)
        invoice1.action_post()

        wiz.create_invoices()
        invoice2 = self.so1.invoice_ids[1]
        invoice2.with_context(check_move_validity=False).invoice_line_ids[
            0
        ].quantity = 0.01
        invoice2.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].quantity = 0.01
        # Invoicing more that the subtotal amount
        invoice2.with_context(check_move_validity=False).invoice_line_ids[
            0
        ].price_unit = 2500.0
        invoice2.with_context(check_move_validity=False).invoice_line_ids[
            1
        ].price_unit = -2500.0
        self.assertEqual(self.so1.order_line[1].amount_invoiced, 45.0)
        self.assertEqual(self.so1.order_line[2].amount_invoiced, -45.0)
        self.assertEqual(self.so1.order_line[1].amount_to_invoice, -5.0)
        self.assertEqual(self.so1.order_line[2].amount_to_invoice, 5.0)
        lines = self.so1._get_invoiceable_lines()
        self.assertEqual(len(lines), 0)
