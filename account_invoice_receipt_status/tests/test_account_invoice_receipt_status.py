# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.purchase.tests.test_purchase_invoice import TestPurchaseToInvoiceCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceReceiptStatus(TestPurchaseToInvoiceCommon):
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
        PurchaseOrderLine = cls.env["purchase.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseOrderLine.create(
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
        PurchaseOrderLine.create(
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

        cls.picking = cls.po.picking_ids
        cls.picking.action_assign()
        cls.move_line = cls.picking.move_line_ids.filtered(
            lambda ml: ml.product_id == cls.product_order
        )
        # create vendor bill from the purchase order
        action = cls.po.action_create_invoice()
        cls.vendor_bill = cls.env["account.move"].browse(action["res_id"])
        cls.vendor_bill_line_product = cls.vendor_bill.invoice_line_ids.filtered(
            lambda line: line.product_id == cls.product_order
        )
        cls.vendor_bill_line_service = cls.vendor_bill.invoice_line_ids.filtered(
            lambda line: line.product_id == cls.service_order
        )

    def test_initial_status(self):
        # a mix of full/pending/False => partial
        self.assertEqual(self.vendor_bill.receipt_status, "partial")
        # product line is pending receipt
        self.assertEqual(self.vendor_bill_line_product.receipt_status, "pending")
        # Service lines with type 'service' do not create stock moves
        # thus have no receipt status
        self.assertFalse(self.vendor_bill_line_service.receipt_status)

    def test_partial_receipt_status(self):
        # Simulate partial receipt of goods
        self.move_line.qty_done = 5.0
        wiz_act = self.picking.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()

        self.assertEqual(self.vendor_bill.receipt_status, "partial")
        self.assertEqual(self.vendor_bill_line_product.receipt_status, "partial")

        # if we cancel the remaining moves, the receipt status should be 'full'
        picking = self.po.picking_ids - self.picking
        picking.move_ids._action_cancel()
        self.assertEqual(self.vendor_bill.receipt_status, "full")
        self.assertEqual(self.vendor_bill_line_product.receipt_status, "full")

    def test_full_receipt_status(self):
        # Simulate full receipt of goods
        self.move_line.qty_done = 10.0
        self.picking.button_validate()
        self.assertEqual(self.vendor_bill.receipt_status, "full")
        self.assertEqual(self.vendor_bill_line_product.receipt_status, "full")
