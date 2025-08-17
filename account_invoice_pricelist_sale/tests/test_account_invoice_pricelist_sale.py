# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.account_invoice_pricelist.tests.test_account_move_pricelist import (
    TestAccountMovePricelist,
)


class TestAccountInvoicePricelistSale(TestAccountMovePricelist):
    def test_invoice_create_from_sale(self):
        # Create Sale Order
        self.product.invoice_policy = "order"
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.sale_pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.product_variant_id.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                            "qty_delivered": 5,
                        }
                    )
                ],
            }
        )

        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(
            invoice.pricelist_id,
            order.pricelist_id,
            "Invoice Pricelist has not been recovered from sale order",
        )
