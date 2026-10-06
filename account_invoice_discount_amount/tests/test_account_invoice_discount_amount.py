# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDiscountAmount(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.early_discount_term = cls.env["account.payment.term"].create(
            {
                "name": "2% discount if paid within 10 days",
                "early_discount": True,
                "discount_percentage": 2,
                "discount_days": 10,
                "line_ids": [
                    Command.create(
                        {"value": "percent", "nb_days": 30, "value_amount": 100}
                    )
                ],
            }
        )

    def test_discount_amounts_mirror_the_line_with_a_discount(self):
        """discount_amount_currency/discount_balance mirror the one payment
        line carrying an early payment discount"""
        invoice = self._create_invoice(
            invoice_payment_term_id=self.early_discount_term.id
        )
        discount_line = invoice.line_ids.filtered_domain(
            [("display_type", "=", "payment_term")]
        )
        self.assertEqual(
            invoice.discount_amount_currency, discount_line.discount_amount_currency
        )
        self.assertEqual(invoice.discount_balance, discount_line.discount_balance)

    def test_discount_amounts_empty_without_discount(self):
        """No line carries an early payment discount: discount_amount_currency
        and discount_balance stay empty rather than summing plain amounts"""
        invoice = self._create_invoice()
        self.assertFalse(invoice.discount_amount_currency)
        self.assertFalse(invoice.discount_balance)
