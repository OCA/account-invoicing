# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged

from odoo.addons.purchase.tests.test_purchase_invoice import TestPurchaseToInvoiceCommon


@tagged("post_install", "-at_install")
class TestPurchaseInvoicingAutoUpdateQty(TestPurchaseToInvoiceCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po = (
            cls.env["purchase.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": cls.partner_a.id,
                }
            )
        )
        cls.product_order.purchase_method = "receive"
        cls.service_order.purchase_method = "purchase"
        PurchaseOrderLine = cls.env["purchase.order.line"].with_context(
            tracking_disable=True
        )
        cls.po_product_line = PurchaseOrderLine.create(
            {
                "name": cls.product_order.name,
                "product_id": cls.product_order.id,
                "product_qty": 10.0,
                "product_uom": cls.product_order.uom_id.id,
                "price_unit": cls.product_order.list_price,
                "order_id": cls.po.id,
                "taxes_id": False,
            }
        )
        cls.po_service_line = PurchaseOrderLine.create(
            {
                "name": cls.service_order.name,
                "product_id": cls.service_order.id,
                "product_qty": 10.0,
                "product_uom": cls.service_order.uom_id.id,
                "price_unit": cls.service_order.list_price,
                "order_id": cls.po.id,
                "taxes_id": False,
            }
        )
        cls.po.button_confirm()
        # force receipt to force the lines to 'to invoice' state
        cls.po_product_line.qty_received = 1.0

        # create vendor bill from the purchase order
        action = cls.po.action_create_invoice()
        cls.vendor_bill = cls.env["account.move"].browse(action["res_id"])
        cls.vendor_bill_line_product = cls.vendor_bill.invoice_line_ids.filtered(
            lambda line: line.product_id == cls.product_order
        )
        cls.vendor_bill_line_service = cls.vendor_bill.invoice_line_ids.filtered(
            lambda line: line.product_id == cls.service_order
        )

    def test_initial_bill_quantities(self):
        self.assertEqual(self.vendor_bill.po_invoice_auto_update_qty, False)
        self.assertEqual(
            self.vendor_bill_line_product.quantity,
            1,
        )
        self.assertEqual(
            self.vendor_bill_line_service.quantity,
            10.0,
        )

    def test_no_auto_update_if_disabled(self):
        self.vendor_bill.po_invoice_auto_update_qty = False
        # receive 4 products
        self.po_product_line.qty_received = 4.0
        # check that the vendor bill line quantity is unchanged
        self.assertTrue(self.vendor_bill_line_product)
        self.assertEqual(
            self.vendor_bill_line_product.quantity,
            1.0,
        )

    def test_manual_receive_auto_update_if_enabled(self):
        self.vendor_bill.po_invoice_auto_update_qty = True
        # receive 6 products
        self.po_product_line.qty_received = 6.0
        self.env.flush_all()
        self.assertEqual(self.po_product_line.qty_to_invoice, 0.0)
        # check that the vendor bill line quantity is updated
        self.assertEqual(
            self.vendor_bill_line_product.quantity,
            6.0,
        )
        # receive 4 more products (total received = 10)
        self.po_product_line.qty_received = 10.0
        self.env.flush_all()
        self.assertEqual(self.po_product_line.qty_to_invoice, 0.0)
        # check that the vendor bill line quantity is updated
        self.assertEqual(
            self.vendor_bill_line_product.quantity,
            10.0,
        )
        # decrease received products to 8
        self.po_product_line.qty_received = 8.0
        self.env.flush_all()
        self.assertEqual(self.po_product_line.qty_to_invoice, 0.0)
        # check that the vendor bill line quantity is updated
        self.assertEqual(
            self.vendor_bill_line_product.quantity,
            8.0,
        )

    def test_stock_receive_auto_update_enabled(self):
        self.vendor_bill.po_invoice_auto_update_qty = True
        self.picking = self.po.picking_ids
        self.picking.action_assign()
        self.move_line = self.picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_order
        )
        self.move_line.qty_done = 5.0
        wiz_act = self.picking.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()
        self.env.flush_all()
        self.assertEqual(self.po_product_line.qty_to_invoice, 0.0)
        # check that the vendor bill line quantity is updated
        self.assertEqual(
            self.vendor_bill_line_product.quantity,
            5.0,
        )
        backoder = self.picking.backorder_ids
        backoder.action_assign()
        backorder_move_line = backoder.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_order
        )
        backorder_move_line.qty_done = 5.0
        wiz_act = backoder.button_validate()
        self.env.flush_all()
        self.assertEqual(self.po_product_line.qty_to_invoice, 0.0)
        # check that the vendor bill line quantity is updated
        self.assertEqual(
            self.vendor_bill_line_product.quantity,
            10.0,
        )

    def test_auto_update_setting(self):
        # enable the setting on the company via res.config.settings
        self.env["res.config.settings"].create(
            {"po_invoice_auto_update_qty": True}
        ).set_values()
        # this does not impact existing vendor bills
        self.assertEqual(self.vendor_bill.po_invoice_auto_update_qty, False)
        # if we create a new vendor bill, it should have the setting enabled
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_a.id,
            }
        )
        self.assertEqual(invoice.po_invoice_auto_update_qty, True)
        # if we disable it on the company, new vendor bills should have it disabled
        self.env["res.config.settings"].create(
            {"po_invoice_auto_update_qty": False}
        ).set_values()
        invoice2 = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_a.id,
            }
        )
        self.assertEqual(invoice2.po_invoice_auto_update_qty, False)
