# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestComparePrice(SavepointCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.Sale_o = self.env["sale.order"]
        self.Invoice_o = self.env["account.invoice"]
        self.Pricelist_o = self.env["product.pricelist"]
        self.FisPos_o = self.env["account.fiscal.position"]

        self.at_receivable = self.env["account.account.type"].create({
            "name": "Test receivable account",
            "type": "receivable",
        })
        self.a_receivable = self.env["account.account"].create({
            "name": "Test receivable account",
            "code": "TEST_RA",
            "user_type_id": self.at_receivable.id,
            "reconcile": True,
        })
        self.product = self.env["product.product"].create({
            "name": "Product Test",
            "type": "service",
            "list_price": 100.00,
        })
        self.pricelist_id = self.Pricelist_o.create({
            "name": "Test Sale pricelist",
            "item_ids": [(0, 0, {
                    "applied_on": "0_product_variant",
                    "compute_price": "fixed",
                    "fixed_price": 300.00,
                    "product_id": self.product.id,
                })],
        })
        self.partner = self.env["res.partner"].create({
            "name": "Test Partner",
            "property_product_pricelist": self.pricelist_id.id,
            "property_account_receivable_id": self.a_receivable.id,
        })

        self.invoice = self.Invoice_o.create({
            "partner_id": self.partner.id,
            "account_id": self.a_receivable.id,
            "type": "out_invoice",
            "invoice_line_ids": [
                (0, 0, {
                    "account_id": self.a_receivable.id,
                    "product_id": self.product.id,
                    "name": "Test line",
                    "quantity": 1.0,
                    "price_unit": 0,
                }),
            ],
        })
        self.sale = self.Sale_o.create({
            "partner_id": self.partner.id,
            "order_line": [
                (0, 0, {
                    "product_id": self.product.id,
                    "name": "Test line",
                    "product_uom_qty": 1.0,
                    "price_unit": 0,
                }),
            ],
        })

    def test_sale_pricelist(self):
        self.sale.onchange_partner_id()
        self.assertEqual(
            self.sale.pricelist_id,
            self.sale.partner_id.property_product_pricelist)

    def test_account_invoice_pricelist(self):
        self.invoice._onchange_partner_id_account_invoice_pricelist()
        self.assertEqual(
            self.invoice.pricelist_id,
            self.invoice.partner_id.property_product_pricelist)
        self.assertEqual(self.invoice.pricelist_id, self.pricelist_id)

    def test_compare_prices(self):
        self.sale.order_line[0].product_id_change()
        self.invoice.invoice_line_ids[0]._onchange_product_id()
        self.assertEqual(
            self.sale.order_line[0].price_unit,
            self.invoice.invoice_line_ids[0].price_unit,
            "Price with sale and invoice are different : "
            "Sale %s and Invoice %s" %
            (self.sale.order_line[0].price_unit,
             self.invoice.invoice_line_ids[0].price_unit))
