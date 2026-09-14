# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from datetime import timedelta

from odoo import Command, fields
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDiscountDate(AccountTestInvoicingCommon):
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

    def test_discount_date_from_payment_term(self):
        """An early discount payment term sets discount_date automatically"""
        invoice = self._create_invoice(
            invoice_payment_term_id=self.early_discount_term.id
        )
        self.assertTrue(invoice.discount_date)
        self.assertLess(invoice.discount_date, invoice.invoice_date_due)

    def test_discount_date_empty_without_discount(self):
        """No early discount applies: discount_date stays empty"""
        invoice = self._create_invoice()
        self.assertFalse(invoice.discount_date)

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

    def test_discount_date_propagation(self):
        """Test discount date is propagated properly to invoice lines"""
        normal_discount_date = fields.Date.today() + timedelta(days=5)
        early_discount_date = fields.Date.today() + timedelta(days=3)
        for move_type in {"out_invoice", "in_invoice"}:
            with self.subTest(move_type=move_type):
                invoice = self._create_invoice(move_type=move_type)
                # Check inverse
                invoice.discount_date = normal_discount_date
                for date_due_line in invoice.line_ids.filtered("date_maturity"):
                    self.assertEqual(date_due_line.discount_date, invoice.discount_date)
                    self.assertEqual(invoice.discount_date, normal_discount_date)
                # Check computed
                early_discount_date = fields.Date.today() + timedelta(days=3)
                invoice.line_ids.filtered("date_maturity")[
                    :1
                ].discount_date = early_discount_date
                self.assertEqual(invoice.discount_date, early_discount_date)
