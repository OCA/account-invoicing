# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


class TestInvoiceModeMonthly(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.SaleOrder = cls.env["sale.order"]

    def test_late_invoicing_for_last_month(self):
        """Check that last month invoicing will be done if missed."""
        company = self.env.company
        company.invoicing_mode_monthly_day_todo = 31
        company.invoicing_mode_monthly_last_execution = "2020-05-31"
        self.assertTrue(self.env.company)
        with freeze_time("2020-07-03"):
            res = self.SaleOrder._company_monthly_invoicing_today()
            self.assertTrue(res)
        company.invoicing_mode_monthly_last_execution = "2020-06-30"
        with freeze_time("2020-07-03"):
            res = self.SaleOrder._company_monthly_invoicing_today()
            self.assertFalse(res)

    def test_selected_day_not_exist_in_month(self):
        """Check on last day of the month invoicing is done.

        The day of invoicing selected could not exist in the current
        month, but invoicing should still be executed on the last
        day of the month.
        """
        company = self.env.company
        company.invoicing_mode_monthly_day_todo = 31
        company.invoicing_mode_monthly_last_execution = "2020-05-29"
        self.assertTrue(self.env.company)
        with freeze_time("2020-06-29"):
            res = self.SaleOrder._company_monthly_invoicing_today()
            self.assertFalse(res)
        with freeze_time("2020-06-30"):
            res = self.SaleOrder._company_monthly_invoicing_today()
            self.assertTrue(res)

    def test_no_invoicing_done_yet(self):
        """Check when is the first monthly invoicing done.

        When monthly invoicing has never been done, it will not be run
        for the previous month.
        """
        company = self.env.company
        company.invoicing_mode_monthly_day_todo = 15
        company.invoicing_mode_monthly_last_execution = None
        self.assertTrue(self.env.company)
        with freeze_time("2020-06-11"):
            res = self.SaleOrder._company_monthly_invoicing_today()
            self.assertFalse(res)
        with freeze_time("2020-06-30"):
            res = self.SaleOrder._company_monthly_invoicing_today()
            self.assertTrue(res)
