# Copyright 2026 Studio73 - Vicent Castells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestCrmTagLink(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag_1 = cls.env["crm.tag"].create({"name": "Tag 1"})
        cls.tag_2 = cls.env["crm.tag"].create({"name": "Tag 2"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
            }
        )

    def test_crm_tag_propagation(self):
        """Test that CRM tags are correctly propagated from SO to invoice."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "tag_ids": [Command.set([self.tag_1.id, self.tag_2.id])],
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
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        self.assertEqual(invoice.crm_tag_ids, sale_order.tag_ids)
        for line in invoice.invoice_line_ids:
            self.assertEqual(line.crm_tag_ids, sale_order.tag_ids)

    def test_prepare_invoice_line_direct(self):
        """Test the manual preparation of invoice lines with tags."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "tag_ids": [Command.set([self.tag_1.id])],
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                        }
                    )
                ],
            }
        )
        line = sale_order.order_line[0]
        vals = line._prepare_invoice_line()
        self.assertIn("crm_tag_ids", vals)
        self.assertEqual(vals["crm_tag_ids"][0][2], [self.tag_1.id])
