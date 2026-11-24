# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import TestTaxCommon


@tagged("post_install", "-at_install")
class TestFixedAmountMultiplierJs(TestTaxCommon):
    """Test fixed amount multiplier parity between Python and JS."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dozen_uom = cls.env.ref("uom.product_uom_dozen")
        cls.unit_uom = cls.env.ref("uom.product_uom_unit")

    def _jsonify_tax(self, tax):
        values = super()._jsonify_tax(tax)
        values["fixed_amount_multiplier"] = tax.fixed_amount_multiplier
        return values

    def test_multiplier_none_zero_quantity(self):
        """Test no multiplier applies the fixed amount once on zero quantity."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 5 none zero quantity",
                "amount_type": "fixed",
                "amount": 5.0,
                "fixed_amount_multiplier": "none",
                "type_tax_use": "sale",
            }
        )
        self.assert_taxes_computation(
            tax,
            price_unit=100.0,
            quantity=0.0,
            expected_values={
                "total_excluded": 0.0,
                "total_included": 5.0,
                "taxes_data": [
                    (0.0, 5.0),
                ],
            },
        )
        self._run_js_tests()

    def test_multiplier_quantity(self):
        """Explicit quantity multiplier (default behavior) - JS parity."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 5 quantity",
                "amount_type": "fixed",
                "amount": 5.0,
                "fixed_amount_multiplier": "quantity",
                "type_tax_use": "sale",
            }
        )
        self.assert_taxes_computation(
            tax,
            price_unit=100.0,
            quantity=10,
            expected_values={
                "total_excluded": 1000.0,
                "total_included": 1050.0,
                "taxes_data": [
                    (1000.0, 50.0),
                ],
            },
        )
        self._run_js_tests()

    def test_multiplier_none(self):
        """No multiplier: amount once per line - JS parity."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 5 none",
                "amount_type": "fixed",
                "amount": 5.0,
                "fixed_amount_multiplier": "none",
                "type_tax_use": "sale",
            }
        )
        self.assert_taxes_computation(
            tax,
            price_unit=100.0,
            quantity=10,
            expected_values={
                "total_excluded": 1000.0,
                "total_included": 1005.0,
                "taxes_data": [
                    (1000.0, 5.0),
                ],
            },
        )
        self._run_js_tests()

    def test_multiplier_product_quantity_dozen(self):
        """1 Dozen -> 12 units - JS parity."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 5 product_quantity",
                "amount_type": "fixed",
                "amount": 5.0,
                "fixed_amount_multiplier": "product_quantity",
                "type_tax_use": "sale",
            }
        )
        product = self._create_product(uom_id=self.unit_uom.id)
        # 1 dozen = 12 units -> 12 * 5 = 60
        self.assert_taxes_computation(
            tax,
            price_unit=100.0,
            quantity=1,
            expected_values={
                "total_excluded": 100.0,
                "total_included": 160.0,
                "taxes_data": [
                    (100.0, 60.0),
                ],
            },
            product=product,
            product_uom=self.dozen_uom,
        )
        self._run_js_tests()

    def test_multiplier_product_weight(self):
        """Product weight: product_quantity x weight x amount - JS parity."""
        tax = self.env["account.tax"].create(
            {
                "name": "Fixed 3 product_weight",
                "amount_type": "fixed",
                "amount": 3.0,
                "fixed_amount_multiplier": "product_weight",
                "type_tax_use": "sale",
            }
        )
        product = self._create_product(uom_id=self.unit_uom.id, weight=2.5)
        # 10 units * 2.5 kg * 3.0 = 75
        self.assert_taxes_computation(
            tax,
            price_unit=100.0,
            quantity=10,
            expected_values={
                "total_excluded": 1000.0,
                "total_included": 1075.0,
                "taxes_data": [
                    (1000.0, 75.0),
                ],
            },
            product=product,
        )
        self._run_js_tests()
