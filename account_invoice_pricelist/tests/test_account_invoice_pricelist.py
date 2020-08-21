# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountMovePricelist(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountMove = cls.env["account.move"]
        cls.ProductPricelist = cls.env["product.pricelist"]
        cls.FiscalPosition = cls.env["account.fiscal.position"]
        cls.fiscal_position = cls.FiscalPosition.create(
            {"name": "Test Fiscal Position", "active": True}
        )
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test sale journal", "type": "sale", "code": "TEST_SJ"}
        )
        cls.at_receivable = cls.env["account.account.type"].create(
            {
                "name": "Test receivable account",
                "type": "receivable",
                "internal_group": "income",
            }
        )
        cls.a_receivable = cls.env["account.account"].create(
            {
                "name": "Test receivable account",
                "code": "TEST_RA",
                "user_type_id": cls.at_receivable.id,
                "reconcile": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_product_pricelist": 1,
                "property_account_receivable_id": cls.a_receivable.id,
                "property_account_position_id": cls.fiscal_position.id,
            }
        )
        cls.product = cls.env["product.template"].create(
            {"name": "Product Test", "list_price": 100.00}
        )
        cls.sale_pricelist = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 300.00,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.invoice = cls.AccountMove.create(
            {
                "partner_id": cls.partner.id,
                "type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.product_variant_ids[:1].id,
                            "name": "Test line",
                            "quantity": 1.0,
                            "price_unit": 100.00,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.product_variant_ids[:2].id,
                            "name": "Test line 2",
                            "quantity": 1.0,
                            "price_unit": 100.00,
                        },
                    ),
                ],
            }
        )

    def test_account_invoice_pricelist(self):
        self.invoice._onchange_partner_id_account_invoice_pricelist()
        self.assertEqual(
            self.invoice.pricelist_id,
            self.invoice.partner_id.property_product_pricelist,
        )

    def test_account_invoice_change_pricelist(self):
        self.invoice.pricelist_id = self.sale_pricelist.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 300.00)
