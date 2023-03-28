#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestRefund(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.receipt = cls.init_invoice(
            "out_receipt",
            post=True,
            amounts=[
                10.0,
            ],
        )
        cls.invoice = cls.init_invoice(
            "out_invoice",
            post=True,
            amounts=[
                10.0,
            ],
        )

    def test_receipt_is_receipt(self):
        self.assertTrue(self.receipt.is_receipt())

    def test_invoice_is_not_receipt(self):
        self.assertFalse(self.invoice.is_receipt())
