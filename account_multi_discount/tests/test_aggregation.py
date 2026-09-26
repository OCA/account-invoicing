# Copyright 2026 Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAggregateDiscountDistribution(TransactionCase):
    """Pure-formula tests on the ``_aggregate_discount_distribution`` helper.

    The helper is exposed as a ``@staticmethod`` on ``account.move.line`` and
    is the single source of truth for discount aggregation across this
    module and any downstream module. Validating it independently means the
    other tests can focus on integration concerns.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountMoveLine = cls.env["account.move.line"]

    def _agg(self, distribution):
        return self.AccountMoveLine._aggregate_discount_distribution(distribution)

    def test_none_returns_zero(self):
        self.assertEqual(self._agg(None), 0.0)

    def test_empty_list_returns_zero(self):
        self.assertEqual(self._agg([]), 0.0)

    def test_false_returns_zero(self):
        self.assertEqual(self._agg(False), 0.0)

    def test_single_zero_discount(self):
        self.assertEqual(self._agg([0]), 0.0)

    def test_single_ten_percent(self):
        self.assertAlmostEqual(self._agg([10]), 10.0, places=10)

    def test_single_full_discount(self):
        self.assertAlmostEqual(self._agg([100]), 100.0, places=10)

    def test_single_negative_discount(self):
        self.assertAlmostEqual(self._agg([-10]), -10.0, places=10)

    def test_two_discounts_compose_multiplicatively(self):
        self.assertAlmostEqual(self._agg([10, 5]), 14.5, places=10)

    def test_three_discounts(self):
        self.assertAlmostEqual(self._agg([10, 5, 2]), 16.21, places=10)

    def test_zero_in_middle_is_neutral(self):
        self.assertAlmostEqual(
            self._agg([10, 0, 5]),
            self._agg([10, 5]),
            places=10,
        )

    def test_order_independent_for_pure_percentages(self):
        self.assertAlmostEqual(
            self._agg([10, 5, 2]),
            self._agg([2, 5, 10]),
            places=10,
        )

    def test_two_fifty_percents_total_seventy_five(self):
        self.assertAlmostEqual(self._agg([50, 50]), 75.0, places=10)

    def test_none_value_in_list_treated_as_zero(self):
        self.assertAlmostEqual(self._agg([10, None, 5]), 14.5, places=10)
