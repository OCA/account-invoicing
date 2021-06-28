# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


class TestInvoiceModeWeekly(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.SaleOrder = cls.env["sale.order"]

    def test_late_invoicing_for_last_week(self):
        """Check that last week invoicing will be done if missed."""
        company = self.env.company
        company.invoicing_mode_weekly_day_todo = "4"  # Friday
        company.invoicing_mode_weekly_last_execution = "2020-07-02"
        self.assertTrue(self.env.company)
        with freeze_time("2020-07-03"):
            res = self.SaleOrder._company_weekly_invoicing_today()
            self.assertTrue(res)
        company.invoicing_mode_weekly_last_execution = "2020-07-04"
        with freeze_time("2020-07-03"):
            res = self.SaleOrder._company_weekly_invoicing_today()
            self.assertFalse(res)

    def test_no_invoicing_done_yet(self):
        """Check when is the first weekly invoicing done.

        When weekly invoicing has never been done, it will not be run
        for the previous week.
        """
        company = self.env.company
        company.invoicing_mode_weekly_day_todo = "0"  # Monday
        company.invoicing_mode_weekly_last_execution = None
        self.assertTrue(self.env.company)
        with freeze_time("2020-06-07"):
            res = self.SaleOrder._company_weekly_invoicing_today()
            self.assertFalse(res)
        with freeze_time("2020-06-08"):
            res = self.SaleOrder._company_weekly_invoicing_today()
            self.assertTrue(res)
