# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests import common
from odoo.tools.float_utils import float_compare


class TestSaleTimesheetDescription(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleTimesheetDescription, cls).setUpClass()

        # Make sure user is in English
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
        cls.product_uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.product_uom_day = cls.env.ref("uom.product_uom_day")

        # Make sure the UoM's have the necessary properties for the rounding
        # effects on the quantities in the unit tests do work as expected.
        # Note: Need to write the (new) reference UoM first.
        cls.product_uom_day.write(
            {
                "uom_type": "reference",
                "factor": 1.0,
                "rounding": 0.01,
            }
        )
        cls.product_uom_hour.write(
            {
                "uom_type": "smaller",
                "factor": 8.0,
                "rounding": 0.01,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
                "uom_id": cls.product_uom_hour.id,
                "uom_po_id": cls.product_uom_hour.id,
                "service_type": "timesheet",
                "invoice_policy": "delivery",
                # Task created on cls.project when the cls.product is ordered
                "service_tracking": "task_global_project",
                "project_id": cls.project.id,
            }
        )
        # For some reason, using `copy()` does copy the product template, but
        # seemingly not the variant. Hence, we use `create()` again.
        cls.product_two = cls.env["product.product"].create(
            {
                "name": "Test product 2",
                "type": "service",
                "uom_id": cls.product_uom_hour.id,
                "uom_po_id": cls.product_uom_hour.id,
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
        cls.sale_order.timesheet_invoice_split = False

        cls.sale_order_2 = cls.sale_order.copy()

        cls.so_line = cls.env["sale.order.line"].create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 10.5,
                "product_uom": cls.product_uom_hour.id,
                "price_unit": cls.product.list_price,
                "order_id": cls.sale_order.id,
            },
        )
        cls.so_line.product_id_change()

        cls.so_2_line_1 = cls.so_line.copy(
            {
                "order_id": cls.sale_order_2.id,
            }
        )
        cls.so_2_line_1.product_id_change()
        cls.so_2_line_2 = cls.so_line.copy(
            {
                "name": cls.product_two.name,
                "product_id": cls.product_two.id,
                "product_uom_qty": 2.5,
                # "product_uom": cls.product_uom_hour.id,
                # "price_unit": cls.product.list_price,
                "order_id": cls.sale_order_2.id,
            },
        )
        cls.so_2_line_2.product_id_change()

        # Confirm sales orders, tasks are created
        cls.sale_order.action_confirm()
        cls.sale_order_2.action_confirm()

        cls.task = cls.env["project.task"].search(
            [("sale_line_id", "=", cls.so_line.id)]
        )
        cls.task_2_1 = cls.env["project.task"].search(
            [("sale_line_id", "=", cls.so_2_line_1.id)]
        )
        cls.task_2_2 = cls.env["project.task"].search(
            [("sale_line_id", "=", cls.so_2_line_2.id)]
        )

        # Add a timesheet to each tasks
        cls.timesheet = cls.env["account.analytic.line"].create(
            {
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "date": datetime.strptime("2017-08-04", "%Y-%m-%d"),
                "name": "Test description 1234567890",
                "product_uom_id": cls.product_uom_hour.id,
                "unit_amount": 10.5,
                "user_id": cls.env.user.id,
            }
        )
        # Note that for copies, we need to explicitly assign the correct
        # sale.order.line, namely the one from the 'task_id', as copying just
        # copies the value from the original, i.e. the one from the original's
        # 'task_id'. This could be done by simply calling `_compute_so_line()`.
        cls.timesheet_2_1 = cls.timesheet.copy(
            {
                "task_id": cls.task_2_1.id,
                "name": "Test description 2.1",
            }
        )
        cls.timesheet_2_1._compute_so_line()
        cls.timesheet_2_2 = cls.timesheet.copy(
            {
                "task_id": cls.task_2_2.id,
                "name": "Test description 2.2",
                "unit_amount": 2.5,
            }
        )
        cls.timesheet_2_2._compute_so_line()

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
            "Test product\n2017-08-04 - 10.5 Hours - Test description 1234567890",
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
            "011", "Test product\n10.5 Hours - Test description 1234567890"
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

    def test_two_timesheets_different_dates(self):
        self.sale_order.timesheet_invoice_description = "111"
        expected = "Test product\n2017-08-04 - 10.5 Hours - Test description 1234567890"

        # Add a new timesheet to the same invoiced sale.order.line (i.e. with the same
        # task and projet) but with different date
        self.env["account.analytic.line"].create(
            {
                "project_id": self.project.id,
                "task_id": self.task.id,
                "date": datetime.strptime("2018-08-04", "%Y-%m-%d"),
                "name": "Timesheet 2",
                "product_uom_id": self.product_uom_hour.id,
                "unit_amount": 10.5,
                "user_id": self.env.user.id,
            }
        )

        invoice = self.sale_order.with_context(
            test_timesheet_description=True
        )._create_invoices(start_date="2017-01-01", end_date="2018-01-01")

        self.assertEqual(invoice.invoice_line_ids[0].name, expected)

    def test_two_timesheets_same_date_join(self):
        self.sale_order.timesheet_invoice_description = "111"
        description = "2017-08-04 - 10.5 Hours - Test description 1234567890"
        expected = "Test product" + 2 * ("\n" + description)

        # Add a new timesheet with the same date to the same invoiced sale.order.line
        self.timesheet2 = self.timesheet.copy()

        invoice = self.sale_order.with_context(
            test_timesheet_description=True
        )._create_invoices(start_date="2017-01-01", end_date="2018-01-01")

        self.assertEqual(invoice.invoice_line_ids[0].name, expected)

    def test_three_timesheets_same_date_split(self):
        self.sale_order.timesheet_invoice_split = True
        self.sale_order.timesheet_invoice_description = "001"
        # Set a different UoM on SO line/Invoice line from Timesheets UoM
        new_uom = self.product_uom_day
        new_qty = self.so_line.product_uom._compute_quantity(
            self.so_line.product_uom_qty, new_uom
        )
        self.so_line.product_uom = new_uom.id
        self.so_line.product_uom_qty = new_qty
        self.so_line.product_uom_change()  # to adjust the unit price

        # Add a new timesheets with the same date to the same invoiced sale.order.line
        self.timesheet.write({"name": "Description 1"})
        self.timesheet2 = self.timesheet.copy(
            {
                "name": "Description 2",
                "date": datetime.strptime("2017-08-05", "%Y-%m-%d"),
            }
        )
        self.timesheet3 = self.timesheet.copy(
            {
                "name": "Description 3",
                "date": datetime.strptime("2017-08-06", "%Y-%m-%d"),
            }
        )

        invoice = self.sale_order.with_context(
            test_timesheet_description=True
        )._create_invoices(start_date="2017-01-01", end_date="2018-01-01")

        self.assertEqual(len(invoice.invoice_line_ids), 4)
        # Initially this test was added in order to adapt to this
        # change in Odoo:
        # https://github.com/odoo/odoo/pull/115907
        # self.assertEqual(
        #     sum(self.sale_order.mapped("order_line.qty_delivered")), 3.93)
        # However, the change was reverted, because unknown reason:
        # https://github.com/odoo/odoo/pull/122431
        # Decide to comment the test just for the record.

        # First line is a section with product's name
        aml_ids = invoice.invoice_line_ids.sorted(key=lambda aml: aml.sequence)
        first_aml = aml_ids[0]
        self.assertEqual(first_aml.display_type, "line_section")
        self.assertEqual(first_aml.name, "Test product")

        # 2 first aml refer to timesheet and timesheet2
        self.assertEqual(aml_ids[1].name, "Description 1")
        self.assertEqual(aml_ids[1].quantity, 1.32)
        self.assertEqual(aml_ids[2].name, "Description 2")
        self.assertEqual(aml_ids[2].quantity, 1.32)

        # Last aml quantity is calculated as the rest to equal the original aml quantity
        self.assertEqual(aml_ids[-1].name, "Description 3")
        # Reason of change above
        self.assertEqual(aml_ids[-1].quantity, 1.3)

        # Invoice lines total must equal the expected order line's delivered and
        # invoiced quantities
        aml_sum = sum(aml.quantity for aml in aml_ids[1:])
        pr = self.so_line.product_uom.rounding
        self.assertTrue(
            float_compare(aml_sum, self.so_line.qty_delivered, precision_rounding=pr)
            == 0
        )
        self.assertTrue(
            float_compare(aml_sum, self.so_line.qty_invoiced, precision_rounding=pr)
            == 0
        )

    def test_three_plus_two_timesheets_split(self):
        self.sale_order_2.timesheet_invoice_split = True
        self.sale_order_2.timesheet_invoice_description = "001"
        # Set a different UoM on sale order line / invoice line from
        # timesheet's UoM, but only for the first line = first product / task.
        new_uom = self.product_uom_day
        new_qty = self.so_2_line_1.product_uom._compute_quantity(
            self.so_2_line_1.product_uom_qty, new_uom
        )
        self.so_2_line_1.product_uom = new_uom.id
        self.so_2_line_1.product_uom_qty = new_qty
        self.so_2_line_1.product_uom_change()  # to adjust the unit price

        # Add two new timesheets to the first invoiced sale order line
        self.timesheet_2_1.write({"name": "Description 1"})
        self.timesheet_2_1.copy(
            {
                "name": "Description 2",
                "date": datetime.strptime("2017-08-05", "%Y-%m-%d"),
            }
        )
        self.timesheet_2_1.copy(
            {
                "name": "Description 3",
                "date": datetime.strptime("2017-08-06", "%Y-%m-%d"),
            }
        )
        # Add one new timesheet to the second invoiced sale order line
        self.timesheet_2_2.write({"name": "Description 11"})
        self.timesheet_2_2.copy(
            {
                "name": "Description 12",
                "date": datetime.strptime("2017-08-05", "%Y-%m-%d"),
            }
        )

        invoice = self.sale_order_2.with_context(
            test_timesheet_description=True
        )._create_invoices(start_date="2017-01-01", end_date="2018-01-01")

        self.assertEqual(len(invoice.invoice_line_ids), 7)

        # === First product, i.e. first task ===
        # First line is a section with product's name
        aml_ids = invoice.invoice_line_ids.sorted(key=lambda aml: aml.sequence)
        self.assertEqual(aml_ids[0].display_type, "line_section")
        self.assertEqual(aml_ids[0].name, "Test product")
        # Next line refers to first timesheet
        self.assertEqual(aml_ids[1].name, "Description 1")
        self.assertEqual(aml_ids[1].quantity, 1.32)
        # Next line refers to first timesheet's first copy
        self.assertEqual(aml_ids[2].name, "Description 2")
        self.assertEqual(aml_ids[2].quantity, 1.32)
        # Next line refers to first timesheet's second copy, and its quantity
        # is calculated as the rest to equal the original line's quantity
        self.assertEqual(aml_ids[3].name, "Description 3")
        self.assertEqual(aml_ids[3].quantity, 1.3)

        # Invoice lines total must equal the expected order line's delivered and
        # invoiced quantities
        line = self.so_2_line_1
        pr = line.product_uom.rounding
        self.assertEqual(
            float_compare(3.94, line.qty_delivered, precision_rounding=pr), 0
        )
        self.assertEqual(
            float_compare(3.94, line.qty_invoiced, precision_rounding=pr), 0
        )

        # === Second product, i.e. second task ===
        # Next line is a section with product's name
        # aml_ids = invoice.invoice_line_ids.sorted(key=lambda aml: aml.sequence)
        self.assertEqual(aml_ids[4].display_type, "line_section")
        self.assertEqual(aml_ids[4].name, "Test product 2")
        # Next line refer to second timesheet
        self.assertEqual(aml_ids[5].name, "Description 11")
        self.assertEqual(aml_ids[5].quantity, 2.5)
        # Next line refers to second timesheet's copy, and its quantity is
        # calculated as the rest to equal the original line's quantity
        self.assertEqual(aml_ids[6].name, "Description 12")
        self.assertEqual(aml_ids[6].quantity, 2.5)

        # Invoice lines total must equal the expected order line's delivered
        # and invoiced quantities
        line = self.so_2_line_2
        pr = line.product_uom.rounding
        self.assertEqual(
            float_compare(5.0, line.qty_delivered, precision_rounding=pr), 0
        )
        self.assertEqual(
            float_compare(5.0, line.qty_invoiced, precision_rounding=pr), 0
        )
