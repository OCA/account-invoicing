# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import TestTaxCommon


@tagged("post_install", "-at_install")
class TestFixedAmountCurrencyJs(TestTaxCommon):
    """Test fixed amount currency conversion parity between Python and JS."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_currency = cls.env.company.currency_id
        cls.other_currency = cls.setup_other_currency(
            "EUR", rates=[(fields.Date.today(), 0.50)]
        )

    def _jsonify_tax(self, tax):
        values = super()._jsonify_tax(tax)
        values["currency_id"] = tax.currency_id.id if tax.currency_id else False
        values["currency_rate"] = tax.currency_rate
        return values

    def test_fixed_amount_no_currency(self):
        """Standard fixed tax without currency (JS parity)."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 10",
                "amount_type": "fixed",
                "amount": 10.0,
                "type_tax_use": "sale",
            }
        )
        self.assert_taxes_computation(
            tax,
            price_unit=100.0,
            quantity=5,
            expected_values={
                "total_excluded": 500.0,
                "total_included": 550.0,
                "taxes_data": [
                    (500.0, 50.0),
                ],
            },
        )
        self._run_js_tests()

    def test_fixed_amount_company_currency(self):
        """Fixed tax in company currency on company currency doc (JS parity)."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 10 company",
                "amount_type": "fixed",
                "amount": 10.0,
                "currency_id": self.company_currency.id,
                "type_tax_use": "sale",
            }
        )
        self.assert_taxes_computation(
            tax,
            price_unit=100.0,
            quantity=5,
            expected_values={
                "total_excluded": 500.0,
                "total_included": 550.0,
                "taxes_data": [
                    (500.0, 50.0),
                ],
            },
        )
        self._run_js_tests()

    def test_fixed_amount_currency_conversion(self):
        """Fixed tax in company currency, document in EUR (JS parity)."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 10 company",
                "amount_type": "fixed",
                "amount": 10.0,
                "currency_id": self.company_currency.id,
                "type_tax_use": "sale",
            }
        )
        # rate=0.50 means 1 company = 0.50 EUR
        # Tax = 5 * 10 company = 50 company → 50 * 0.50 = 25 EUR
        document = self.populate_document(
            self.init_document(
                lines=[
                    {
                        "price_unit": 100.0,
                        "quantity": 5,
                        "tax_ids": tax,
                    },
                ],
                currency=self.other_currency,
                rate=0.50,
            )
        )
        self.assert_base_lines_tax_details(
            document,
            {
                "base_lines_tax_details": [
                    {
                        "total_excluded_currency": 500.0,
                        "total_excluded": 1000.0,
                        "total_included_currency": 525.0,
                        "total_included": 1050.0,
                        "delta_total_excluded_currency": 0.0,
                        "delta_total_excluded": 0.0,
                        "manual_total_excluded": None,
                        "manual_total_excluded_currency": None,
                        "manual_tax_amounts": None,
                        "taxes_data": [
                            {
                                "tax_id": tax.id,
                                "tax_amount_currency": 25.0,
                                "tax_amount": 50.0,
                                "base_amount_currency": 500.0,
                                "base_amount": 1000.0,
                            },
                        ],
                    },
                ],
            },
        )
        self._run_js_tests()
