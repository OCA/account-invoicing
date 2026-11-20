# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestFixedAmountCurrency(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_currency = cls.env.company.currency_id
        cls.other_currency = cls.setup_other_currency(
            "EUR", rates=[(fields.Date.today(), 0.50)]
        )
        cls.third_currency = cls.setup_other_currency(
            "GBP", rates=[(fields.Date.today(), 0.40)]
        )
        cls.fixed_tax_company_currency = cls.env["account.tax"].create(
            {
                "name": "Fixed in company currency",
                "amount_type": "fixed",
                "amount": 10.0,
                "currency_id": cls.company_currency.id,
                "type_tax_use": "sale",
            }
        )
        cls.fixed_tax_other_currency = cls.env["account.tax"].create(
            {
                "name": "Fixed in other currency",
                "amount_type": "fixed",
                "amount": 10.0,
                "currency_id": cls.other_currency.id,
                "type_tax_use": "sale",
            }
        )
        cls.fixed_tax_no_currency = cls.env["account.tax"].create(
            {
                "name": "Fixed no currency",
                "amount_type": "fixed",
                "amount": 10.0,
                "type_tax_use": "sale",
            }
        )
        cls.product = cls._create_product(name="Test Product", lst_price=100.0)

    def _get_tax_amount(self, invoice, tax):
        return abs(invoice.line_ids.filtered(lambda ln: ln.tax_line_id == tax).balance)

    def _get_tax_amount_currency(self, invoice, tax):
        return abs(
            invoice.line_ids.filtered(lambda ln: ln.tax_line_id == tax).amount_currency
        )

    # -------------------------------------------------------------------------
    # No currency set (standard behavior)
    # -------------------------------------------------------------------------

    def test_fixed_amount_no_currency(self):
        """Standard behavior when currency_id is not set."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_no_currency,
        )
        # Standard fixed: 5 * 10 = 50
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_no_currency), 50.0, places=2
        )

    def test_fixed_amount_no_currency_foreign_invoice(self):
        """Standard behavior with foreign currency invoice, no currency on tax."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_no_currency,
            currency_id=self.other_currency,
        )
        # Standard fixed: 5 * 10 = 50 in document currency
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_no_currency),
            50.0,
            places=2,
        )

    # -------------------------------------------------------------------------
    # Tax currency == document currency (no conversion)
    # -------------------------------------------------------------------------

    def test_fixed_amount_same_as_doc_currency(self):
        """Tax in company currency on company currency invoice → no conversion."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_company_currency,
        )
        # 5 * 10 = 50 in company currency
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_company_currency),
            50.0,
            places=2,
        )

    def test_fixed_amount_same_as_doc_currency_foreign(self):
        """Tax in EUR on EUR invoice → no conversion needed."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_other_currency,
            currency_id=self.other_currency,
        )
        # 5 * 10 = 50 EUR (tax and doc are both EUR)
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_other_currency),
            50.0,
            places=2,
        )

    def test_fixed_amount_same_as_doc_currency_custom_rate(self):
        """Tax in EUR on EUR invoice with custom rate → no conversion.

        Even though the invoice has a manual exchange rate, the tax amount
        must not be converted because the tax currency matches the document
        currency.
        """
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_other_currency,
            currency_id=self.other_currency,
            invoice_currency_rate=0.75,
        )
        # Verify the custom rate is effective on the product line
        product_line = invoice.invoice_line_ids
        self.assertAlmostEqual(product_line.currency_rate, 0.75, places=2)
        # The product line should reflect the custom rate:
        # amount_currency = 500 EUR, balance = 500 / 0.75 = 666.67
        self.assertAlmostEqual(product_line.amount_currency, -500.0, places=2)
        self.assertAlmostEqual(product_line.balance, -666.67, places=2)
        # Tax: 5 * 10 = 50 EUR — no conversion despite the custom rate
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_other_currency),
            50.0,
            places=2,
        )

    # -------------------------------------------------------------------------
    # Tax currency == company currency, document in foreign currency
    # -------------------------------------------------------------------------

    def test_fixed_amount_company_currency_foreign_invoice(self):
        """Tax in company currency, invoice in EUR → convert."""
        # Rate: 1 company_currency = 0.50 EUR
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_company_currency,
            currency_id=self.other_currency,
        )
        # Tax = 5 * 10 = 50 company currency
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_company_currency),
            50.0,
            places=2,
        )
        # Document currency: 50 * 0.50 = 25 EUR
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_company_currency),
            25.0,
            places=2,
        )

    def test_fixed_amount_company_currency_foreign_invoice_custom_rate(self):
        """Tax in company currency, invoice in EUR with custom rate.

        The custom rate must be used for the conversion instead of the
        market rate.
        """
        # Market rate is 0.50, but we force 0.75
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_company_currency,
            currency_id=self.other_currency,
            invoice_currency_rate=0.75,
        )
        # Verify the custom rate is effective
        product_line = invoice.invoice_line_ids
        self.assertAlmostEqual(product_line.currency_rate, 0.75, places=2)
        # Tax = 5 * 10 = 50 company currency
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_company_currency),
            50.0,
            places=2,
        )
        # Document currency: 50 * 0.75 = 37.50 EUR (uses custom rate, not 0.50)
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_company_currency),
            37.50,
            places=2,
        )

    def test_fixed_amount_company_currency_foreign_invoice_past_date(self):
        """Tax in company currency, invoice in EUR dated in the past.

        The tax currency rate must use the invoice date, not today.
        """
        today = fields.Date.today()
        past_date = today - timedelta(days=30)
        with mute_logger("odoo.models.unlink"):
            self.other_currency.rate_ids.unlink()
        self.env["res.currency.rate"].create(
            [
                {
                    "currency_id": self.other_currency.id,
                    "name": past_date,
                    "rate": 0.80,
                },
                {
                    "currency_id": self.other_currency.id,
                    "name": today,
                    "rate": 0.50,
                },
            ]
        )
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_company_currency,
            currency_id=self.other_currency,
            invoice_date=past_date,
        )
        # Tax = 5 * 10 = 50 company currency
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_company_currency),
            50.0,
            places=2,
        )
        # Document currency should use the past rate (0.80), not today (0.50)
        # 50 * 0.80 = 40 EUR
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_company_currency),
            40.0,
            places=2,
        )

    # -------------------------------------------------------------------------
    # Tax currency is a third currency (not company, not document)
    # -------------------------------------------------------------------------

    def test_fixed_amount_third_currency(self):
        """Tax in EUR, invoice in GBP, company in USD → two-step conversion."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_other_currency,
            currency_id=self.third_currency,
        )
        # Tax amount = 10 EUR per unit, qty = 5
        # EUR → company: 10 / 0.50 = 20 company per unit
        # Company total: 5 * 20 = 100 company
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_other_currency),
            100.0,
            places=2,
        )
        # Company → GBP: 100 * 0.40 = 40 GBP
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_other_currency),
            40.0,
            places=2,
        )

    def test_fixed_amount_third_currency_custom_rate(self):
        """Tax in EUR, invoice in GBP with custom rate, company in USD.

        The custom rate (company→GBP) must be used for the final conversion
        step, while the EUR→company conversion still uses the market rate.
        """
        # Market rate for GBP is 0.40, but we force 0.60
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_other_currency,
            currency_id=self.third_currency,
            invoice_currency_rate=0.60,
        )
        # Verify the custom rate is effective
        product_line = invoice.invoice_line_ids
        self.assertAlmostEqual(product_line.currency_rate, 0.60, places=2)
        # Tax amount = 10 EUR per unit, qty = 5
        # EUR → company: 10 / 0.50 = 20 company per unit (market rate)
        # Company total: 5 * 20 = 100 company
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_other_currency),
            100.0,
            places=2,
        )
        # Company → GBP: 100 * 0.60 = 60 GBP (custom rate, not 0.40)
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_other_currency),
            60.0,
            places=2,
        )

    def test_fixed_amount_third_currency_past_date(self):
        """Tax in EUR, invoice in GBP dated in the past.

        The EUR→company conversion must use the rate at the invoice date.
        """
        today = fields.Date.today()
        past_date = today - timedelta(days=30)
        with mute_logger("odoo.models.unlink"):
            self.other_currency.rate_ids.unlink()
        self.env["res.currency.rate"].create(
            [
                {
                    "currency_id": self.other_currency.id,
                    "name": past_date,
                    "rate": 0.80,
                },
                {
                    "currency_id": self.other_currency.id,
                    "name": today,
                    "rate": 0.50,
                },
            ]
        )
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_other_currency,
            currency_id=self.third_currency,
            invoice_date=past_date,
        )
        # Tax = 10 EUR per unit, qty = 5
        # EUR → company at past_date: 10 / 0.80 = 12.50 company per unit
        # Company total: 5 * 12.50 = 62.50 company
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.fixed_tax_other_currency),
            62.50,
            places=2,
        )
        # Company → GBP: 62.50 * 0.40 = 25.0 GBP
        self.assertAlmostEqual(
            self._get_tax_amount_currency(invoice, self.fixed_tax_other_currency),
            25.0,
            places=2,
        )

    # -------------------------------------------------------------------------
    # Credit note
    # -------------------------------------------------------------------------

    def test_fixed_amount_credit_note(self):
        """Currency conversion works on credit notes too."""
        credit_note = self._create_invoice_one_line(
            move_type="out_refund",
            product_id=self.product,
            price_unit=100.0,
            quantity=5,
            tax_ids=self.fixed_tax_company_currency,
            currency_id=self.other_currency,
        )
        self.assertAlmostEqual(
            self._get_tax_amount(credit_note, self.fixed_tax_company_currency),
            50.0,
            places=2,
        )
        self.assertAlmostEqual(
            self._get_tax_amount_currency(credit_note, self.fixed_tax_company_currency),
            25.0,
            places=2,
        )
