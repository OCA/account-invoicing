# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestPurchaseOrderInvoicingGroupingCriteria(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.partner2 = self.env["res.partner"].create({"name": "Other partner"})
        self.product = self.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
                "purchase_method": "purchase",
                "standard_price": 50.00,
            }
        )
        self.GroupingCriteria = self.env["purchase.invoicing.grouping.criteria"]
        self.grouping_criteria_break_partner = self.GroupingCriteria.create(
            {
                "name": "By purchase",
                "field_ids": [
                    (4, self.env.ref("purchase.field_purchase_order__id").id)
                ],
            }
        )
        self.grouping_criteria_group_by_origin = self.GroupingCriteria.create(
            {
                "name": "By origin",
                "field_ids": [
                    (4, self.env.ref("purchase.field_purchase_order__origin").id)
                ],
            }
        )
        self.purchase_order_1 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "origin": "test-0001",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_po_id.id,
                        },
                    )
                ],
            }
        )
        self.purchase_order_1.button_confirm()
        self.purchase_order_2 = self.purchase_order_1.copy(
            {
                "origin": "test-0001",
            }
        )
        self.purchase_order_2.button_confirm()
        self.purchase_order_3 = self.purchase_order_1.copy(
            {
                "partner_id": self.partner2.id,
                "origin": "test-0001",
            }
        )
        self.purchase_order_3.button_confirm()

    def _get_invoice_from_action(self, action):
        if action.get("res_id", False):
            moves = self.env["account.move"].browse(action["res_id"])
        elif "domain" in action:
            moves = self.env["account.move"].search(action["domain"])
        return moves

    def test_invoicing_grouping_default(self):
        action = (
            self.purchase_order_1 + self.purchase_order_2 + self.purchase_order_3
        ).action_create_invoice()
        invoice_ids = self._get_invoice_from_action(action)
        self.assertEqual(len(invoice_ids), 2)
        self.assertEqual(
            self.purchase_order_1.invoice_ids, self.purchase_order_2.invoice_ids
        )

    def test_invoicing_grouping_company_criteria(self):
        """Force create one vendor bill by puerchase order."""
        self.purchase_order_1.company_id.default_purchase_invoicing_grouping_criteria_id = (
            self.grouping_criteria_break_partner.id
        )
        action = (
            self.purchase_order_1 + self.purchase_order_2 + self.purchase_order_3
        ).action_create_invoice()
        invoice_ids = self._get_invoice_from_action(action)
        self.assertEqual(len(invoice_ids), 3)
        self.assertNotEqual(
            self.purchase_order_1.invoice_ids, self.purchase_order_2.invoice_ids
        )

    def test_invoicing_grouping_partner_criteria(self):
        self.partner.purchase_invoicing_grouping_criteria_id = (
            self.grouping_criteria_break_partner.id
        )
        action = (self.purchase_order_1 + self.purchase_order_2).action_create_invoice()
        invoice_ids = self._get_invoice_from_action(action)
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(
            self.purchase_order_1.invoice_ids, self.purchase_order_2.invoice_ids
        )

    def test_invoicing_grouping_company_criteria_origin(self):
        """Real group by other field. In this case by po origin"""
        self.purchase_order_1.company_id.default_purchase_invoicing_grouping_criteria_id = (
            self.grouping_criteria_group_by_origin.id
        )
        action = (
            self.purchase_order_1 + self.purchase_order_2 + self.purchase_order_3
        ).action_create_invoice()
        invoice_ids = self._get_invoice_from_action(action)
        self.assertEqual(len(invoice_ids), 2)
        self.assertEqual(
            self.purchase_order_1.invoice_ids, self.purchase_order_2.invoice_ids
        )
