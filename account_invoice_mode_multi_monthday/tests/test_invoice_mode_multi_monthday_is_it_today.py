# Copyright 2022 Aures TIC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


class TestInvoiceModeMultiMonthday(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.SaleOrder = cls.env["sale.order"]

    def test_invoicing(self):
        company = self.env.company
        company.invoicing_mode_multi_monthday_days = "10,25"
        self.assertTrue(self.env.company)
        with freeze_time("2022-06-9"):
            res = self.SaleOrder._company_multi_monthday_invoicing_today()
            self.assertFalse(res)
        with freeze_time("2022-06-10"):
            res = self.SaleOrder._company_multi_monthday_invoicing_today()
            self.assertTrue(res)
        with freeze_time("2022-06-11"):
            res = self.SaleOrder._company_multi_monthday_invoicing_today()
            self.assertFalse(res)
        with freeze_time("2022-06-25"):
            res = self.SaleOrder._company_multi_monthday_invoicing_today()
            self.assertTrue(res)
