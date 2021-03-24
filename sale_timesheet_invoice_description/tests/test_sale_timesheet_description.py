# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests import common


class TestSaleTimesheetDescription(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleTimesheetDescription, cls).setUpClass()
        # Make sure user is in English
        cls.env["res.lang"].load_lang("en_US")
        cls.env.user.lang = "en_US"
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test analytic account"}
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test project",
                "analytic_account_id": cls.analytic_account.id,
                "allow_timesheets": True,
                "allow_billable": True,
            }
        )
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
                "uom_id": cls.product_uom.id,
                "service_type": "timesheet",
                "invoice_policy": "delivery",
                # Task created on cls.project when the cls.product is ordered
                "service_tracking": "task_global_project",
                "project_id": cls.project.id,
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.so_line = cls.env["sale.order.line"].create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 10.5,
                "product_uom": cls.product.uom_id.id,
                "price_unit": cls.product.list_price,
                "order_id": cls.sale_order.id,
            },
        )
        cls.so_line.product_id_change()
        # confirm SO, task is created
        cls.sale_order.action_confirm()
        cls.task = cls.env["project.task"].search(
            [("sale_line_id", "=", cls.so_line.id)]
        )
        # Add cls.timesheet to this task
        cls.timesheet = cls.env["account.analytic.line"].create(
            {
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "date": datetime.strptime("2017-08-04", "%Y-%m-%d"),
                "name": "Test description 1234567890",
                "product_uom_id": cls.product_uom.id,
                "unit_amount": 10.5,
                "user_id": cls.env.user.id,
            }
        )

    def _test_sale_time_description(self, desc_option, expected):
        self.sale_order.timesheet_invoice_description = desc_option

        invoice = self.sale_order.with_context(
            test_timesheet_description=True
        )._create_invoices()
        self.assertEqual(invoice.line_ids[0].name, expected)

        # Add a new timesheet to the same invoiced sale.order.line
        self.timesheet2 = self.timesheet.copy()

        invoice2 = self.sale_order.with_context(
            test_timesheet_description=True
        )._create_invoices()
        self.assertEqual(invoice2.line_ids[0].name, expected)

    def test_sale_timesheet_description_000(self):
        self._test_sale_time_description("000", "Test product")

    def test_sale_timesheet_description_111(self):
        self._test_sale_time_description(
            "111",
            "Test product\n2017-08-04 - 10.5 Units - Test description 1234567890",
        )

    def test_sale_timesheet_description_101(self):
        self._test_sale_time_description(
            "101", "Test product\n2017-08-04 - Test description 1234567890"
        )

    def test_sale_timesheet_description_001(self):
        self._test_sale_time_description(
            "001", "Test product\nTest description 1234567890"
        )

    def test_sale_timesheet_description_011(self):
        self._test_sale_time_description(
            "011", "Test product\n10.5 Units - Test description 1234567890"
        )

    def test_settings(self):
        settings = self.env["res.config.settings"].create({})
        settings.default_timesheet_invoice_description = "101"
        settings.execute()
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "pricelist_id": self.partner.property_product_pricelist.id,
            }
        )
        self.assertEqual(sale_order.timesheet_invoice_description, "101")

    def test_two_timesheets_same_date(self):
        self.sale_order.timesheet_invoice_description = "111"
        description = "2017-08-04 - 10.5 Units - Test description 1234567890"
        expected = "Test product" + 2 * ("\n" + description)

        # Add a new timesheet with the same date to the same invoiced sale.order.line
        self.timesheet2 = self.timesheet.copy()

        invoice = self.sale_order.with_context(
            test_timesheet_description=True
        )._create_invoices(start_date="2017-01-01", end_date="2018-01-01")

        self.assertEqual(invoice.invoice_line_ids[0].name, expected)

    def test_two_timesheets_different_dates(self):
        self.sale_order.timesheet_invoice_description = "111"
        expected = "Test product\n2017-08-04 - 10.5 Units - Test description 1234567890"

        # Add a new timesheet to the same invoiced sale.order.line (i.e. with the same
        # task and projet) but with different date
        self.env["account.analytic.line"].create(
            {
                "project_id": self.project.id,
                "task_id": self.task.id,
                "date": datetime.strptime("2018-08-04", "%Y-%m-%d"),
                "name": "Timesheet 2",
                "product_uom_id": self.product_uom.id,
                "unit_amount": 10.5,
                "user_id": self.env.user.id,
            }
        )

        invoice = self.sale_order.with_context(
            test_timesheet_description=True
        )._create_invoices(start_date="2017-01-01", end_date="2018-01-01")

        self.assertEqual(invoice.invoice_line_ids[0].name, expected)
