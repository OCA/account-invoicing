# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestModule(BaseCommon):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.product = self.env["product.product"].create({"name": "Test Product"})
        self.product.invoice_policy = "order"

    def _create_sale_order(self, pricelist=False):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist and pricelist.id or False,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                            "qty_delivered": 5,
                        },
                    )
                ],
            }
        )

    def test_invoice_with_pricelist(self):
        """Test invoice creation with pricelist in sale order"""
        pricelist = self.env["product.pricelist"].create({"name": "Demo Pricelist"})
        order = self._create_sale_order(pricelist=pricelist)
        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(
            invoice.pricelist_id,
            order.pricelist_id,
            "Invoice Pricelist has not been recovered from sale order",
        )

    def test_invoice_without_pricelist(self):
        """Test invoice creation without pricelist in sale order"""
        order = self._create_sale_order()
        order.action_confirm()
        invoice = order._create_invoices()
        default_pricelist = self.env["product.pricelist"].search([], limit=1)
        self.assertEqual(
            invoice.pricelist_id,
            default_pricelist,
            "Invoice should have the Default Pricelist",
        )

    def test_invoice_pricelist_inverse(self):
        """Test invoice creation without pricelist but partner has one"""
        partner_pricelist = self.env["product.pricelist"].create(
            {"name": "Partner Specific Pricelist"}
        )
        self.partner.property_product_pricelist = partner_pricelist
        order = self._create_sale_order()
        order.action_confirm()
        invoice = order._create_invoices()
        # Clear invoice pricelist to trigger inverse method
        invoice.pricelist_id = False
        self.assertEqual(
            invoice.pricelist_id,
            partner_pricelist,
            "Invoice should have partner's pricelist when no pricelist is set",
        )
