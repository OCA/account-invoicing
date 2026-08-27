# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form, common, tagged


@tagged("post_install", "-at_install")
class TestPurchaseLineRefundToInvoiceQty(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Basic data: Partner and Product
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "purchase_method": "purchase",
                "standard_price": 100.0,
            }
        )
        ReversalReason = cls.env.get("account.reversal.reason")
        cls.reversal_reason = (
            ReversalReason.search([], limit=1) if ReversalReason else False
        )

        # Create Purchase Order (PO) with 10 units
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.po.button_confirm()
        cls.po_line = cls.po.order_line[0]

        # Create and post the original vendor bill
        invoice_res = cls.po.action_create_invoice()
        cls.invoice = cls.env["account.move"].browse(invoice_res["res_id"])
        cls.invoice.invoice_date = fields.Date.today()
        cls.invoice.action_post()

    def test_01_refund_not_to_reinvoice(self):
        """If 'Not reinvoice' is marked, the invoiced qty should NOT decrease."""
        wizard_ctx = {
            "active_model": "account.move",
            "active_ids": [self.invoice.id],
        }
        with Form(
            self.env["account.move.reversal"].with_context(**wizard_ctx)
        ) as wizard_form:
            wizard_form.journal_id = self.invoice.journal_id
            # Set reason_id if it's required by the environment
            if self.reversal_reason:
                wizard_form.reason_id = self.reversal_reason
            wizard_form.purchase_qty_to_reinvoice = False
            wizard = wizard_form.save()

        res = wizard.reverse_moves()
        refund_invoice = self.env["account.move"].browse(res["res_id"])
        refund_invoice.invoice_date = fields.Date.today()
        refund_invoice.action_post()

        self.po_line._compute_qty_invoiced()
        self.assertEqual(self.po_line.qty_invoiced, 10.0)
        self.assertEqual(self.po_line.qty_refunded_not_invoiceable, 10.0)

    def test_02_refund_standard_behavior(self):
        """If 'Reinvoice' is marked, invoiced qty should decrease (Standard)."""
        wizard_ctx = {
            "active_model": "account.move",
            "active_ids": [self.invoice.id],
        }
        with Form(
            self.env["account.move.reversal"].with_context(**wizard_ctx)
        ) as wizard_form:
            wizard_form.journal_id = self.invoice.journal_id
            if self.reversal_reason:
                wizard_form.reason_id = self.reversal_reason
            wizard_form.purchase_qty_to_reinvoice = True
            wizard = wizard_form.save()

        res = wizard.reverse_moves()
        refund_invoice = self.env["account.move"].browse(res["res_id"])
        refund_invoice.invoice_date = fields.Date.today()
        refund_invoice.action_post()

        self.po_line._compute_qty_invoiced()
        self.assertEqual(self.po_line.qty_invoiced, 0.0)

    def test_03_manual_toggle_on_line(self):
        """Verify manual checkbox toggle on the invoice line."""
        wizard_ctx = {"active_model": "account.move", "active_ids": [self.invoice.id]}
        with Form(
            self.env["account.move.reversal"].with_context(**wizard_ctx)
        ) as wizard_form:
            wizard_form.journal_id = self.invoice.journal_id
            if self.reversal_reason:
                wizard_form.reason_id = self.reversal_reason
            wizard_form.purchase_qty_to_reinvoice = True
            wizard = wizard_form.save()

        res = wizard.reverse_moves()
        refund_invoice = self.env["account.move"].browse(res["res_id"])
        refund_invoice.invoice_date = fields.Date.today()
        refund_invoice.action_post()

        refund_line = refund_invoice.line_ids.filtered(
            lambda x: x.display_type == "product"
        )
        refund_line.write({"purchase_qty_to_reinvoice": False})

        self.po_line._compute_qty_invoiced()
        self.assertEqual(self.po_line.qty_invoiced, 10.0)
