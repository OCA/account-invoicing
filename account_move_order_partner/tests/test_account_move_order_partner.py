# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestAccountMoveOrderPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env["res.partner"].create({"name": "Customer A"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Customer B"})
        cls.invoice_partner = cls.env["res.partner"].create({"name": "Invoice Partner"})
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.env.company.invoice_group_by_order_partner = True

    def _create_sale_order(self, customer, invoice_partner):
        order = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "partner_invoice_id": invoice_partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def test_single_sale_order_invoice(self):
        so = self._create_sale_order(self.partner1, self.invoice_partner)
        so._create_invoices()
        self.assertEqual(len(so.invoice_ids), 1)
        self.assertEqual(so.invoice_ids.order_partner_id, self.partner1)

    def test_two_sales_different_customer_same_invoice_partner(self):
        so1 = self._create_sale_order(self.partner1, self.invoice_partner)
        so2 = self._create_sale_order(self.partner2, self.invoice_partner)
        (so1 + so2)._create_invoices()
        self.assertEqual(so1.invoice_ids.order_partner_id, self.partner1)
        self.assertEqual(so2.invoice_ids.order_partner_id, self.partner2)

    def test_two_sales_same_customer_and_invoice_partner(self):
        so1 = self._create_sale_order(self.partner1, self.invoice_partner)
        so2 = self._create_sale_order(self.partner1, self.invoice_partner)
        (so1 + so2)._create_invoices()
        self.assertEqual(so1.invoice_ids.order_partner_id, self.partner1)
        self.assertEqual(so2.invoice_ids.order_partner_id, self.partner1)
        self.assertEqual(so1.invoice_ids, so2.invoice_ids)

    def test_invoice_group_by_order_partner(self):
        self.env.company.invoice_group_by_order_partner = False
        so1 = self._create_sale_order(self.partner1, self.invoice_partner)
        so2 = self._create_sale_order(self.partner2, self.invoice_partner)
        (so1 + so2)._create_invoices()
        self.assertEqual(so1.invoice_ids, so2.invoice_ids)
        self.assertEqual(so1.invoice_ids.order_partner_id, self.invoice_partner)
