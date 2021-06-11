# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon


class TestInvoiceRefundLine(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.in_invoice = cls.init_invoice("in_invoice")
        cls.in_invoice.post()
        cls.out_invoice = cls.init_invoice("out_invoice")
        cls.out_invoice.post()

    def test_partial_refund_in_invoice(self):
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.in_invoice.id,
                active_model=self.in_invoice._name,
                active_ids=self.in_invoice.ids,
            )
            .create({})
        )
        self.assertEqual(
            reversal.selectable_invoice_lines_ids, self.in_invoice.invoice_line_ids,
        )
        line = self.in_invoice.invoice_line_ids[0]
        reversal.write({"refund_method": "refund_lines", "line_ids": [(4, line.id)]})
        action = reversal.reverse_moves()
        refund = self.env[action["res_model"]].browse(action["res_id"])
        self.assertTrue(refund)
        self.assertEqual(refund._name, "account.move")
        self.assertEqual(1, len(refund.invoice_line_ids))
        self.assertEqual(line.product_id, refund.invoice_line_ids.product_id)
        self.assertNotEqual(
            (self.in_invoice.invoice_line_ids - line).product_id,
            refund.invoice_line_ids.product_id,
        )
        self.assertNotEqual(refund.amount_total, self.out_invoice.amount_total)

    def test_total_refund_in_invoice(self):
        """Checking the old functionality"""
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.in_invoice.id,
                active_model=self.in_invoice._name,
                active_ids=self.in_invoice.ids,
            )
            .create({})
        )
        action = reversal.reverse_moves()
        refund = self.env[action["res_model"]].browse(action["res_id"])
        self.assertTrue(refund)
        self.assertEqual(refund._name, "account.move")
        self.assertEqual(2, len(refund.invoice_line_ids))
        self.assertEqual(refund.amount_total, self.in_invoice.amount_total)

    def test_partial_refund_out_invoice(self):
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.out_invoice.id,
                active_model=self.out_invoice._name,
                active_ids=self.out_invoice.ids,
            )
            .create({})
        )
        self.assertEqual(
            reversal.selectable_invoice_lines_ids, self.out_invoice.invoice_line_ids,
        )
        line = self.out_invoice.invoice_line_ids[0]
        reversal.write({"refund_method": "refund_lines", "line_ids": [(4, line.id)]})
        action = reversal.reverse_moves()
        refund = self.env[action["res_model"]].browse(action["res_id"])
        self.assertTrue(refund)
        self.assertEqual(refund._name, "account.move")
        self.assertEqual(1, len(refund.invoice_line_ids))
        self.assertEqual(line.product_id, refund.invoice_line_ids.product_id)
        self.assertNotEqual(
            (self.out_invoice.invoice_line_ids - line).product_id,
            refund.invoice_line_ids.product_id,
        )
        self.assertNotEqual(refund.amount_total, self.out_invoice.amount_total)

    def test_total_refund_out_invoice(self):
        """Checking the old functionality"""
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.out_invoice.id,
                active_model=self.out_invoice._name,
                active_ids=self.out_invoice.ids,
            )
            .create({})
        )
        action = reversal.reverse_moves()
        refund = self.env[action["res_model"]].browse(action["res_id"])
        self.assertTrue(refund)
        self.assertEqual(refund._name, "account.move")
        self.assertEqual(2, len(refund.invoice_line_ids))
        self.assertEqual(refund.amount_total, self.out_invoice.amount_total)
