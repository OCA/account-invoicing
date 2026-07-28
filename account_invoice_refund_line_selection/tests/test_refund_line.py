# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInvoiceRefundLine(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.in_invoice = cls.init_invoice(
            "in_invoice", products=cls.product_a + cls.product_b
        )
        cls.in_invoice._post()
        cls.out_invoice = cls.init_invoice(
            "out_invoice", products=cls.product_a + cls.product_b
        )
        cls.out_invoice._post()

    def _generic_test_after_refund(
        self, source_invoice, reversal_action, partial_refund
    ):
        reversed_lines = (
            source_invoice.invoice_line_ids[0]
            if partial_refund
            else source_invoice.invoice_line_ids
        )
        qty_reversed_lines = len(reversed_lines)

        refund = self.env[reversal_action["res_model"]].browse(
            reversal_action["res_id"]
        )

        self.assertTrue(refund)
        self.assertEqual(refund._name, "account.move")
        self.assertEqual(qty_reversed_lines, len(refund.invoice_line_ids))

        if partial_refund and qty_reversed_lines == 1:
            self.assertNotEqual(refund.amount_total, source_invoice.amount_total)
            self.assertEqual(
                reversed_lines.product_id, refund.invoice_line_ids.product_id
            )
            self.assertNotEqual(
                (source_invoice.invoice_line_ids - reversed_lines).product_id,
                refund.invoice_line_ids.product_id,
            )
        else:
            self.assertEqual(refund.amount_total, source_invoice.amount_total)

    def test_01_partial_refund_in_invoice(self):
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.in_invoice.id,
                active_model=self.in_invoice._name,
                active_ids=self.in_invoice.ids,
            )
            .create(
                {
                    "journal_id": self.in_invoice.journal_id.id,
                }
            )
        )
        self.assertEqual(
            reversal.selectable_invoice_lines_ids,
            self.in_invoice.invoice_line_ids,
        )
        line = self.in_invoice.invoice_line_ids[0]
        reversal.write({"refund_lines": True, "line_ids": [(4, line.id)]})

        self._generic_test_after_refund(self.in_invoice, reversal.reverse_moves(), True)

    def test_02_total_refund_in_invoice(self):
        """Checking the old functionality"""
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.in_invoice.id,
                active_model=self.in_invoice._name,
                active_ids=self.in_invoice.ids,
            )
            .create(
                {
                    "journal_id": self.in_invoice.journal_id.id,
                }
            )
        )

        self._generic_test_after_refund(
            self.in_invoice, reversal.reverse_moves(), False
        )

    def test_03_partial_refund_out_invoice(self):
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.out_invoice.id,
                active_model=self.out_invoice._name,
                active_ids=self.out_invoice.ids,
            )
            .create(
                {
                    "journal_id": self.out_invoice.journal_id.id,
                }
            )
        )
        self.assertEqual(
            reversal.selectable_invoice_lines_ids,
            self.out_invoice.invoice_line_ids,
        )
        line = self.out_invoice.invoice_line_ids[0]
        reversal.write({"refund_lines": True, "line_ids": [(4, line.id)]})

        self._generic_test_after_refund(
            self.out_invoice, reversal.reverse_moves(), True
        )

    def test_04_total_refund_out_invoice(self):
        """Checking the old functionality"""
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.out_invoice.id,
                active_model=self.out_invoice._name,
                active_ids=self.out_invoice.ids,
            )
            .create(
                {
                    "journal_id": self.out_invoice.journal_id.id,
                }
            )
        )

        self._generic_test_after_refund(
            self.out_invoice, reversal.reverse_moves(), False
        )

    def test_05_partial_refund_out_invoice_wiz_form(self):
        line = self.out_invoice.invoice_line_ids[0]
        wiz_reversal_form = Form(
            self.env["account.move.reversal"].with_context(
                active_id=self.out_invoice.id,
                active_model=self.out_invoice._name,
                active_ids=self.out_invoice.ids,
            )
        )
        wiz_reversal_form.journal_id = self.out_invoice.journal_id
        wiz_reversal_form.refund_lines = True
        wiz_reversal_form.line_ids = line
        # check if module account_invoice_refund_reason is installed
        if hasattr(self.env["account.move"], "reason_id"):
            wiz_reversal_form.reason_id = self.env["account.move.refund.reason"].search(
                [], limit=1
            )
        wiz_id = wiz_reversal_form.save()

        self._generic_test_after_refund(self.out_invoice, wiz_id.reverse_moves(), True)
