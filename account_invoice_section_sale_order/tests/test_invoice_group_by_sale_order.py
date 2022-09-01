# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestInvoiceGroupBySaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_1.invoice_policy = "order"
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
                            "product_id": cls.product_1.id,
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
                            "product_id": cls.product_1.id,
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
        """Check invoice is generated  with sale order sections."""
        result = {
            0: "".join([self.order1_p1.name, " - ", self.order1_p1.client_order_ref]),
            1: "order 1 line 1",
            2: "order 1 line 2",
            3: self.order2_p1.name,
            4: "order 2 line 1",
            5: "order 2 line 2",
        }
        invoice_ids = (self.order1_p1 + self.order2_p1)._create_invoices()
        lines = (
            invoice_ids[0]
            .line_ids.sorted("sequence")
            .filtered(lambda r: not r.exclude_from_invoice_tab)
        )
        for idx, line in enumerate(lines):
            self.assertEqual(line.name, result[idx])

    def test_create_invoice_no_section(self):
        """Check invoice for only one sale order

        No need to create sections

        """
        invoice_id = (self.order1_p1)._create_invoices()
        line_sections = invoice_id.line_ids.filtered(
            lambda r: r.display_type == "line_section"
        )
        self.assertEqual(len(line_sections), 0)
