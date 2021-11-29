# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import mock

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase

SECTION_GROUPING_FUNCTION = "odoo.addons.account_invoice_section_sale_order.models.account_move.AccountMoveLine._get_section_grouping"  # noqa
SECTION_NAME_FUNCTION = (
    "odoo.addons.base.models.res_users.Users._get_invoice_section_name"
)


class TestInvoiceGroupBySaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_2 = cls.env.ref("product.product_product_2")
        cls.product_1.invoice_policy = "order"
        cls.product_2.invoice_policy = "order"
        cls.order1_p1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "client_order_ref": "ref123",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "order 1 line 1",
                            "product_id": cls.product_1.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "order 1 line 2",
                            "product_id": cls.product_2.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.order1_p1.action_confirm()
        cls.order2_p1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "order 2 line 1",
                            "product_id": cls.product_1.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "order 2 line 2",
                            "product_id": cls.product_2.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.order2_p1.action_confirm()

    def test_create_invoice(self):
        """ Check invoice is generated  with sale order sections."""
        result = {
            10: (
                "".join([self.order1_p1.name, " - ", self.order1_p1.client_order_ref]),
                "line_section",
            ),
            20: ("order 1 line 1", False),
            30: ("order 1 line 2", False),
            40: (self.order2_p1.name, "line_section"),
            50: ("order 2 line 1", False),
            60: ("order 2 line 2", False),
        }
        invoice_ids = (self.order1_p1 + self.order2_p1)._create_invoices()
        lines = (
            invoice_ids[0]
            .line_ids.sorted("sequence")
            .filtered(lambda r: not r.exclude_from_invoice_tab)
        )
        for line in lines:
            self.assertEqual(line.name, result[line.sequence][0])
            self.assertEqual(line.display_type, result[line.sequence][1])

    def test_create_invoice_no_section(self):
        """Check invoice for only one sale order

        No need to create sections

        """
        invoice_id = (self.order1_p1)._create_invoices()
        line_sections = invoice_id.line_ids.filtered(
            lambda r: r.display_type == "line_section"
        )
        self.assertEqual(len(line_sections), 0)

    def test_unknown_invoice_section_grouping_value(self):
        """Check an error is raised when invoice_section_grouping value is
        unknown
        """
        mock_company_section_grouping = mock.patch.object(
            type(self.env.company),
            "invoice_section_grouping",
            new_callable=mock.PropertyMock,
        )
        with mock_company_section_grouping as mocked_company_section_grouping:
            mocked_company_section_grouping.return_value = "unknown"
            with self.assertRaises(UserError):
                (self.order1_p1 + self.order2_p1)._create_invoices()

    def test_custom_grouping_by_sale_order_user(self):
        """Check custom grouping by sale order user.

        By mocking account.move.line_get_section_grouping and creating
        res.users.get_invoice_section_name, this test ensures custom grouping
        is possible by redefining these functions"""
        demo_user = self.env.ref("base.user_demo")
        admin_user = self.env.ref("base.partner_admin")
        orders = self.order1_p1 + self.order2_p1
        orders.write({"user_id": admin_user.id})
        sale_order_3 = self.order1_p1.copy({"user_id": demo_user.id})
        sale_order_3.order_line[0].name = "order 3 line 1"
        sale_order_3.order_line[1].name = "order 3 line 2"
        sale_order_3.action_confirm()

        with mock.patch(
            SECTION_GROUPING_FUNCTION
        ) as mocked_get_section_grouping, mock.patch(
            SECTION_NAME_FUNCTION, create=True
        ) as mocked_get_invoice_section_name:
            mocked_get_section_grouping.return_value = "sale_line_ids.order_id.user_id"
            mocked_get_invoice_section_name.return_value = "Mocked value from ResUsers"
            invoice = (orders + sale_order_3)._create_invoices()
            result = {
                10: ("Mocked value from ResUsers", "line_section"),
                20: ("order 1 line 1", False),
                30: ("order 1 line 2", False),
                40: ("order 2 line 1", False),
                50: ("order 2 line 2", False),
                60: ("Mocked value from ResUsers", "line_section"),
                70: ("order 3 line 1", False),
                80: ("order 3 line 2", False),
            }
            for line in invoice.invoice_line_ids.sorted("sequence"):
                self.assertEqual(line.name, result[line.sequence][0])
                self.assertEqual(line.display_type, result[line.sequence][1])
