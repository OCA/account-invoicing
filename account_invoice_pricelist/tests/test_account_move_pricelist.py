# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import common


class TestAccountMovePricelist(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.AccountMove = cls.env["account.move"]
        cls.ProductPricelist = cls.env["product.pricelist"]
        cls.FiscalPosition = cls.env["account.fiscal.position"]
        cls.group_discount = cls.env.ref("sale.group_discount_per_so_line")
        cls.fiscal_position = cls.FiscalPosition.create(
            {"name": "Test Fiscal Position", "active": True}
        )
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test sale journal", "type": "sale", "code": "TEST_SJ"}
        )
        # Make sure the currency of the company is USD, as this not always happens
        # To be removed in V17: https://github.com/odoo/odoo/pull/107113
        cls.company = cls.env.company
        cls.env.cr.execute(
            "UPDATE res_company SET currency_id = %s WHERE id = %s",
            (cls.env.ref("base.USD").id, cls.company.id),
        )
        cls.a_receivable = cls.env["account.account"].create(
            {
                "name": "Test receivable account",
                "code": "TESTRA",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.product = cls.env["product.template"].create(
            {"name": "Product Test", "list_price": 100.00}
        )
        cls.product2 = cls.env["product.template"].create(
            {"name": "Product Test 2", "list_price": 100.00}
        )
        cls.product_product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100,
                "taxes_id": False,
            }
        )
        cls.combos = cls.env["product.combo"].create(
            [
                {
                    "name": "Product Combo",
                    "combo_item_ids": [
                        Command.create(
                            {"product_id": cls.product_product.id, "extra_price": 0}
                        )
                    ],
                }
            ]
        )

        cls.product3 = cls.env["product.product"].create(
            {
                "list_price": 100,
                "name": "Desk Combo",
                "type": "combo",
                "taxes_id": False,
                "combo_ids": [(6, 0, [combo.id for combo in cls.combos])],
            }
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
        cls.sale_pricelist2 = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist 2",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 60.00,
                            "product_tmpl_id": cls.product2.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist3 = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist 3",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 0.00,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.sale_pricelist4 = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist 4",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "percent_price": 0.00,
                            "product_tmpl_id": cls.product.id,
                        },
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_product_pricelist": cls.sale_pricelist.id,
                "property_account_receivable_id": cls.a_receivable.id,
                "property_account_position_id": cls.fiscal_position.id,
            }
        )
        cls.sale_pricelist_fixed_without_discount = cls.ProductPricelist.create(
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
        cls.sale_pricelist_with_discount = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 2",
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
        cls.euro_currency = cls.env["res.currency"].search(
            [("active", "=", False), ("name", "=", "EUR")]
        )
        cls.euro_currency.active = True
        cls.usd_currency = cls.env["res.currency"].search([("name", "=", "USD")])
        cls.sale_pricelist_with_discount_in_euros = cls.ProductPricelist.create(
            {
                "name": "Test Sale pricelist - 4",
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
        cls.invoice_combo = cls.AccountMove.create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product3.id,
                            "name": "Test line",
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

    def test_01_account_invoice_pricelist(self):
        self.assertEqual(self.invoice.pricelist_id, self.sale_pricelist)

    def test_02_account_invoice_change_pricelist(self):
        self.env.user.write({"groups_id": [(5, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 60.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_03_account_invoice_pricelist_without_discount(self):
        self.env.user.write({"groups_id": [(4, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist_fixed_without_discount.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 60)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_04_account_invoice_with_discount_change_pricelist(self):
        self.env.user.write({"groups_id": [(5, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist_with_discount.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 90.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_05_account_invoice_without_discount_change_pricelist(self):
        self.env.user.write({"groups_id": [(4, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist_without_discount.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 100.00)
        self.assertEqual(invoice_line.discount, 10.00)

    def test_06_account_invoice_pricelist_with_discount_secondary_currency(self):
        self.env.user.write({"groups_id": [(5, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist_with_discount_in_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertAlmostEqual(invoice_line.price_unit, 75.55)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_07_account_invoice_pricelist_without_discount_secondary_currency(self):
        self.env.user.write({"groups_id": [(4, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist_without_discount_in_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertAlmostEqual(invoice_line.price_unit, 83.94)
        self.assertEqual(invoice_line.discount, 10.00)

    def test_08_account_invoice_fixed_pricelist_with_discount_secondary_currency(self):
        self.env.user.write({"groups_id": [(5, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist_fixed_with_discount_in_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 60.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_09_account_invoice_fixed_pricelist_without_discount_secondary_currency(
        self,
    ):
        self.env.user.write({"groups_id": [(4, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist_fixed_wo_disc_euros.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertAlmostEqual(invoice_line.price_unit, 60)
        self.assertEqual(invoice_line.discount, 0)

    def test_10_check_currency(self):
        with self.assertRaises(UserError):
            self.invoice.with_context(force_check_currecy=True).write(
                {"pricelist_id": self.sale_pricelist_with_discount_in_euros.id}
            )
            self.invoice.with_context(force_check_currecy=True).write(
                {"currency_id": self.usd_currency.id}
            )

    def test_11_account_move_line_without_product(self):
        self.invoice.invoice_line_ids[:1].product_id = False
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 0.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_12_account_invoice_without_pricelist(self):
        self.env.user.write({"groups_id": [(4, self.group_discount.id)]})
        self.invoice.pricelist_id = self.sale_pricelist2.id
        self.invoice.invoice_line_ids[:1]._compute_discount()
        self.assertEqual(self.invoice.invoice_line_ids[:1].discount, 0.0)
        self.invoice.pricelist_id = False
        self.invoice.invoice_line_ids[:1]._compute_discount()
        self.assertEqual(self.invoice.invoice_line_ids[:1].discount, 0.0)

    def test_13_account_invoice_pricelist_with_discount(self):
        self.invoice_combo.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 100.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_14_compute_discount(self):
        self.env.user.write({"groups_id": [(4, self.group_discount.id)]})
        self.product.write({"list_price": 0.00})
        self.invoice.pricelist_id = self.sale_pricelist3.id
        self.invoice.invoice_line_ids[0]._compute_discount()
        self.assertEqual(self.invoice.invoice_line_ids[0].discount, 0.0)
        self.product.write({"list_price": 100.00})
        self.invoice.pricelist_id = self.sale_pricelist4.id
        self.invoice.invoice_line_ids[0]._compute_discount()
        self.assertEqual(self.invoice.invoice_line_ids[0].discount, 0)
