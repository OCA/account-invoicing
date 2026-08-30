# Copyright 2026 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.addons.base.tests.common import BaseCommon


class TestInvoiceModeBiweeklyIsItToday(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.SaleOrder = cls.env["sale.order"]
        # Create a partner with biweekly invoicing mode to ensure the company
        # is picked up by _company_biweekly_invoicing_today()
        cls.env["res.partner"].create(
            {
                "name": "Test Biweekly Partner",
                "invoicing_mode": "biweekly",
                "company_id": cls.company.id,
            }
        )

    def test_biweekly_fixed_days_cycle(self):
        """Check the biweekly invoicing cycle with fixed days."""
        company = self.company
        company.invoicing_mode_biweekly_day_1 = 1
        company.invoicing_mode_biweekly_day_2 = 16
        company.invoicing_mode_biweekly_last_execution = "2024-01-01 10:00:00"

        # Between days
        with freeze_time("2024-01-10"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertNotIn(company, res)

        # On second day
        with freeze_time("2024-01-16"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertIn(company, res)

        # After second day execution
        company.invoicing_mode_biweekly_last_execution = "2024-01-16 10:00:00"
        with freeze_time("2024-01-20"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertNotIn(company, res)

        # On first day of next month
        with freeze_time("2024-02-01"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertIn(company, res)

    def test_biweekly_inverted_days_order(self):
        """Check that the order of days (day 1 vs day 2) does not matter."""
        company = self.company
        # Day 1 is 31, Day 2 is 15 (inverted order)
        company.invoicing_mode_biweekly_day_1 = 31
        company.invoicing_mode_biweekly_day_2 = 15
        company.invoicing_mode_biweekly_last_execution = "2024-01-14 10:00:00"

        # On 15th
        with freeze_time("2024-01-15"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertIn(company, res)

        # After execution on 15th
        company.invoicing_mode_biweekly_last_execution = "2024-01-15 10:00:00"
        with freeze_time("2024-01-20"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertNotIn(company, res)

        # On 31st
        with freeze_time("2024-01-31"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertIn(company, res)

    def test_biweekly_month_end_clamping(self):
        """Check that day 31 works for months with 30 days (clamping)."""
        company = self.company
        company.invoicing_mode_biweekly_day_1 = 31
        company.invoicing_mode_biweekly_day_2 = 15
        company.invoicing_mode_biweekly_last_execution = "2024-06-15 10:00:00"

        # On June 30th (June has 30 days, so 31 should clamp to 30)
        with freeze_time("2024-06-30"):
            res = self.SaleOrder._company_biweekly_invoicing_today()
            self.assertIn(
                company, res, "Should invoice on June 30th if day 31 is configured"
            )
