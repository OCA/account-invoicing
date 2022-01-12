# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestRefundInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.in_refund = cls.init_invoice(
            "in_refund", products=cls.product_a + cls.product_b
        )
        cls.in_refund._post()
        cls.out_refund = cls.init_invoice(
            "out_refund", products=cls.product_a + cls.product_b
        )
        cls.out_refund._post()

    def test_in_refund_reinvoice(self):
        invoice_action = self.in_refund.action_refund_reinvoice()
        invoice = self.env[invoice_action["res_model"]].browse(invoice_action["res_id"])
        self.assertEqual(invoice.move_type, "in_invoice")
        self.assertEqual(
            invoice.amount_total_signed, -self.in_refund.amount_total_signed
        )

    def test_out_refund_reinvoice(self):
        invoice_action = self.out_refund.action_refund_reinvoice()
        invoice = self.env[invoice_action["res_model"]].browse(invoice_action["res_id"])
        self.assertEqual(invoice.move_type, "out_invoice")
        self.assertEqual(
            invoice.amount_total_signed, -self.out_refund.amount_total_signed
        )
