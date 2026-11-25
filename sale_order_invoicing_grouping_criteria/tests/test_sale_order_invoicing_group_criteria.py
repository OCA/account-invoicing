# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests import new_test_user

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestSaleOrderInvoicingGroupingCriteria(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )
        cls.env.user.group_ids |= cls.env.ref(
            "sales_team.group_sale_salesman_all_leads"
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Other partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
                "invoice_policy": "order",
            }
        )
        cls.grouping_criteria = cls.env["sale.invoicing.grouping.criteria"].create(
            {
                "name": "Delivery Address",
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom_id": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.order.action_confirm()
        cls.order2 = cls.order.copy()
        cls.order2.action_confirm()

    def test_invoicing_same_data(self):
        invoice_ids = (self.order + self.order2)._create_invoices()
        self.assertEqual(len(invoice_ids), 1)
        self.assertEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_default(self):
        self.order2.partner_invoice_id = self.partner2.id
        invoice_ids = (self.order + self.order2)._create_invoices()
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_company_criteria(self):
        self.order2.partner_shipping_id = self.partner2.id
        self.order.company_id.default_sale_invoicing_grouping_criteria_id = (
            self.grouping_criteria.id
        )
        invoice_ids = (self.order + self.order2)._create_invoices()
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_partner_criteria(self):
        self.order2.partner_shipping_id = self.partner2.id
        self.partner.sale_invoicing_grouping_criteria_id = self.grouping_criteria.id
        invoice_ids = (self.order + self.order2)._create_invoices()
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_partner_criteria_as_demo(self):
        self.order2.partner_shipping_id = self.partner2.id
        self.partner.sale_invoicing_grouping_criteria_id = self.grouping_criteria.id
        user_demo = new_test_user(
            self.env,
            login="test_demo",
            groups="account.group_account_manager,sales_team.group_sale_salesman_all_leads",
        )
        invoice_ids = (self.order + self.order2).with_user(user_demo)._create_invoices()
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_specific_order_field(self):
        """Regression test for checking values in order, not in invoices vals."""
        self.partner.sale_invoicing_grouping_criteria_id = self.grouping_criteria.id
        self.grouping_criteria["field_ids"] = [
            (4, self.env.ref("sale.field_sale_order__id").id)
        ]
        invoices = (self.order + self.order2)._create_invoices()
        self.assertEqual(len(invoices), 2)

    def test_commercial_field(self):
        self.partner.sale_invoicing_grouping_criteria_id = self.grouping_criteria.id
        children = self.env["res.partner"].create(
            {"name": "Test children", "parent_id": self.partner.id}
        )
        self.assertEqual(
            children.sale_invoicing_grouping_criteria_id, self.grouping_criteria
        )
