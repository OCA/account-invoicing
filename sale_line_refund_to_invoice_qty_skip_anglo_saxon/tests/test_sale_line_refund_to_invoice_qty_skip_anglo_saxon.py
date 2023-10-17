# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo.tests import Form, TransactionCase


class TestSaleLineRefundToInvoiceQtySkipAngloSaxon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "consu"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    ),
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.order.action_confirm()
        cls.order.order_line[0].write({"qty_delivered": 5.0})
        cls.order._create_invoices()
        cls.invoice = cls.order.invoice_ids[0]
        cls.invoice.action_post()
        cls.refund_reason_skip_anglo_saxon = cls.env[
            "account.move.refund.reason"
        ].create(
            {
                "name": "Skip Anglo Saxon Reason",
                "skip_anglo_saxon_entries": True,
            }
        )
        cls.refund_reason_not_skip_anglo_saxon = cls.env[
            "account.move.refund.reason"
        ].create(
            {
                "name": "Not Skip Anglo Saxon Reason",
                "skip_anglo_saxon_entries": False,
            }
        )

    def test_refund_qty_to_reinvoice_skip_anglo_saxon(self):
        context_wizard = {
            "active_model": "account.move",
            "active_ids": self.invoice.ids,
        }
        wizard = (
            self.env["account.move.reversal"]
            .with_context(**context_wizard)
            .create(
                {
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        wizard_form = Form(wizard)
        wizard_form.reason_id = self.refund_reason_skip_anglo_saxon
        self.assertFalse(wizard_form.editable_sale_qty_to_reinvoice)
        self.assertFalse(wizard_form.sale_qty_to_reinvoice)
        self.assertTrue(wizard_form._get_modifier("sale_qty_to_reinvoice", "readonly"))
        wizard_form.reason_id = self.refund_reason_not_skip_anglo_saxon
        self.assertTrue(wizard_form.editable_sale_qty_to_reinvoice)
        self.assertTrue(wizard_form.sale_qty_to_reinvoice)
        self.assertFalse(wizard_form._get_modifier("sale_qty_to_reinvoice", "readonly"))
