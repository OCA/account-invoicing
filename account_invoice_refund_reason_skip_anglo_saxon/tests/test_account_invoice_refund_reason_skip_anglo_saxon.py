# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestAccountInvoiceRefundReasonSkipAngloSaxon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        cls.fifo_category = cls.env["product.category"].create(
            {
                "name": "test_product_ctg",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Fifo Product",
                "list_price": 15.0,
                "standard_price": 10.0,
                "categ_id": cls.fifo_category.id,
                "is_storable": True,
            }
        )
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

    def test_01_refund_skip_anglo_saxon(self):
        invoice_form = Form(
            self.env["account.move"].with_context(
                default_move_type="out_invoice",
                default_journal_id=self.sale_journal.id,
            )
        )
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as invoice_line:
            invoice_line.product_id = self.product
            invoice_line.price_unit = 15.0
            invoice_line.quantity = 5

        invoice = invoice_form.save()
        invoice.invoice_line_ids.account_id = (
            self.fifo_category.property_account_income_categ_id
        )
        invoice.action_post()
        self.assertTrue(
            invoice.invoice_line_ids.filtered(lambda x: x.display_type != "cogs")
        )

        reversal_form = Form(
            self.env["account.move.reversal"].with_context(
                active_ids=invoice.ids,
                active_model="account.move",
            )
        )
        reversal_form.reason_id = self.refund_reason_not_skip_anglo_saxon
        reversal_wizard = reversal_form.save()
        action = reversal_wizard.reverse_moves()
        refund = self.env["account.move"].browse(action.get("res_id"))
        refund.action_post()
        self.assertTrue(refund.line_ids.filtered(lambda x: x.display_type == "cogs"))

        reversal_form = Form(
            self.env["account.move.reversal"].with_context(
                active_ids=invoice.ids,
                active_model="account.move",
            )
        )
        reversal_form.reason_id = self.refund_reason_skip_anglo_saxon
        reversal_wizard = reversal_form.save()
        action = reversal_wizard.reverse_moves()
        refund = self.env["account.move"].browse(action.get("res_id"))
        refund.action_post()
        self.assertFalse(refund.line_ids.filtered(lambda x: x.display_type == "cogs"))
