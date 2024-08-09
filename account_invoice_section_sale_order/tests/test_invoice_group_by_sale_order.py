# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import mock

from odoo.exceptions import UserError

from .common import Common

SECTION_GROUPING_FUNCTION = "odoo.addons.account_invoice_section_sale_order.models.account_move.AccountMoveLine._get_section_grouping"  # noqa
SECTION_NAME_FUNCTION = (
    "odoo.addons.base.models.res_users.Users._get_invoice_section_name"
)


class TestInvoiceGroupBySaleOrder(Common):
    def test_create_invoice(self):
        """Check invoice is generated  with sale order sections."""
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
            if line.sequence not in result:
                continue
            self.assertEqual(line.name, result[line.sequence][0])
            self.assertEqual(line.display_type, result[line.sequence][1])

    def test_create_invoice_with_currency(self):
        """Check invoice is generated with a correct total amount"""
        eur = self.env.ref("base.EUR")
        pricelist = self.env["product.pricelist"].create(
            {"name": "Europe pricelist", "currency_id": eur.id}
        )
        orders = self.order1_p1 | self.order2_p1
        orders.write({"pricelist_id": pricelist.id})
        invoices = orders._create_invoices()
        self.assertEqual(invoices.amount_total, 80)

    def test_create_invoice_with_default_journal(self):
        """Using a specific journal for the invoice should not be broken"""
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        (self.order1_p1 + self.order2_p1).with_context(
            default_journal_id=journal.id
        )._create_invoices()

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
                if line.sequence not in result:
                    continue
                self.assertEqual(line.name, result[line.sequence][0])
                self.assertEqual(line.display_type, result[line.sequence][1])
