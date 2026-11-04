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
        cls.multi_line_term = cls.env["account.payment.term"].create(
            {
                "name": "30% now, 70% in 30 days",
                "line_ids": [
                    Command.create(
                        {"value": "percent", "nb_days": 0, "value_amount": 30}
                    ),
                    Command.create(
                        {"value": "percent", "nb_days": 30, "value_amount": 70}
                    ),
                ],
            }
        )

    def _assert_discount_amounts_mirror_payment_term_line(self, move):
        payment_term_line = move.line_ids.filtered_domain(
            [("display_type", "=", "payment_term")]
        )
        self.assertTrue(payment_term_line.discount_amount_currency)
        self.assertEqual(
            move.discount_amount_currency, payment_term_line.discount_amount_currency
        )
        self.assertEqual(move.discount_balance, payment_term_line.discount_balance)

    def test_discount_amounts_customer_invoice(self):
        """The amounts mirror the payment term line granting the discount"""
        invoice = self._create_invoice(
            invoice_payment_term_id=self.early_discount_term.id
        )
        self._assert_discount_amounts_mirror_payment_term_line(invoice)

    def test_discount_amounts_vendor_bill(self):
        """Bills have negative payment term amounts: they are mirrored too"""
        bill = self._create_invoice(
            move_type="in_invoice",
            invoice_payment_term_id=self.early_discount_term.id,
        )
        self._assert_discount_amounts_mirror_payment_term_line(bill)
        self.assertLess(bill.discount_amount_currency, 0)

    def test_discount_amounts_empty_without_discount(self):
        """Without Early Payment Discount, even with several payment term
        lines, the amounts stay empty"""
        invoice = self._create_invoice(invoice_payment_term_id=self.multi_line_term.id)
        self.assertEqual(invoice.discount_amount_currency, 0.0)
        self.assertEqual(invoice.discount_balance, 0.0)
