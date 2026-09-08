# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReceipt(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.receipt = cls.init_invoice(
            "out_receipt",
            post=True,
            products=cls.product_a,
        )
        cls.invoice = cls.init_invoice(
            "out_invoice",
            post=True,
            products=cls.product_a,
        )

    def test_receipt_is_receipt(self):
        self.assertTrue(self.receipt.is_receipt())

    def test_invoice_is_not_receipt(self):
        self.assertFalse(self.invoice.is_receipt())
