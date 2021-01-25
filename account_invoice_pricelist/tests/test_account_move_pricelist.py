# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import inspect

from odoo.tests import common

from odoo.addons.sale.models.sale import SaleOrderLine as upstream

# if this hash fails then the original function it was copied from
# needs to be checked to see if there are any major changes that
# need to be updated in this module's _get_real_price_currency

VALID_HASHES = ["7c0bb27c20598327008f81aee58cdfb4"]


class TestAccountMovePricelist(common.SavepointCase):
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
                            "fixed_price": 60.00,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist_fixed_without_discount = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist",
                "discount_policy": "without_discount",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 60.00,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist_with_discount = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 2",
                "discount_policy": "with_discount",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist_without_discount = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 3",
                "discount_policy": "without_discount",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.euro_currency = cls.env["res.currency"].search([("name", "=", "EUR")])
        cls.sale_pricelist_with_discount_in_euros = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 4",
                "discount_policy": "with_discount",
                "currency_id": cls.euro_currency.id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist_without_discount_in_euros = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 5",
                "discount_policy": "without_discount",
                "currency_id": cls.euro_currency.id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist_fixed_with_discount_in_euros = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 6",
                "discount_policy": "with_discount",
                "currency_id": cls.euro_currency.id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 60.00,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist_fixed_wo_disc_euros = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 7",
                "discount_policy": "without_discount",
                "currency_id": cls.euro_currency.id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 60.00,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.invoice = cls.AccountMove.create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
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
        # Fix currency rate of EUR -> USD to 1.5289
        usd_currency = cls.env["res.currency"].search([("name", "=", "USD")])
        usd_rates = cls.env["res.currency.rate"].search(
            [("currency_id", "=", usd_currency.id)]
        )
        usd_rates.unlink()
        cls.env["res.currency.rate"].create(
            {
                "currency_id": usd_currency.id,
                "rate": 1.5289,
                "create_date": "2010-01-01",
                "write_date": "2010-01-01",
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
        self.assertEqual(invoice_line.price_unit, 60.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_pricelist_without_discount(self):
        self.invoice.pricelist_id = self.sale_pricelist_fixed_without_discount.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 100.00)
        self.assertEqual(invoice_line.discount, 40.00)

    def test_account_invoice_with_discount_change_pricelist(self):
        self.invoice.pricelist_id = self.sale_pricelist_with_discount.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 90.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_without_discount_change_pricelist(self):
        self.invoice.pricelist_id = self.sale_pricelist_without_discount.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 100.00)
        self.assertEqual(invoice_line.discount, 10.00)

    def test_account_invoice_pricelist_with_discount_secondary_currency(self):
        self.invoice.currency_id = self.euro_currency.id
        self.invoice.pricelist_id = self.sale_pricelist_with_discount_in_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertAlmostEqual(invoice_line.price_unit, 58.87)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_pricelist_without_discount_secondary_currency(self):
        self.invoice.currency_id = self.euro_currency.id
        self.invoice.pricelist_id = self.sale_pricelist_without_discount_in_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertAlmostEqual(invoice_line.price_unit, 65.41)
        self.assertEqual(invoice_line.discount, 10.00)

    def test_account_invoice_fixed_pricelist_with_discount_secondary_currency(self):
        self.invoice.currency_id = self.euro_currency.id
        self.invoice.pricelist_id = self.sale_pricelist_fixed_with_discount_in_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 60.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_fixed_pricelist_without_discount_secondary_currency(self):
        self.invoice.currency_id = self.euro_currency.id
        self.invoice.pricelist_id = self.sale_pricelist_fixed_wo_disc_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertAlmostEqual(invoice_line.price_unit, 65.41)
        self.assertEqual(invoice_line.discount, 8.27)

    def test_upstream_file_hash(self):
        """Test that copied upstream function hasn't received fixes"""
        func = inspect.getsource(upstream._get_real_price_currency).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertIn(func_hash, VALID_HASHES)
