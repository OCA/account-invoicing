# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestAccountMovePricelist(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                force_check_currency=True,
                force_compute_currency=True,
            )
        )
        cls.AccountMove = cls.env["account.move"]
        cls.ProductPricelist = cls.env["product.pricelist"]
        cls.FiscalPosition = cls.env["account.fiscal.position"]
        cls.fiscal_position = cls.FiscalPosition.create(
            {"name": "Test Fiscal Position", "active": True}
        )
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test sale journal", "type": "sale", "code": "TEST_SJ"}
        )
        cls.usd_currency = cls.env.ref("base.USD")
        cls.euro_currency = cls._enable_currency("EUR")
        # Make sure the company works in USD, as this does not always happen.
        cls._use_currency("USD")
        # Fix currency rate of EUR -> USD to 1.5289
        cls.env["res.currency.rate"].search(
            [("currency_id", "=", cls.usd_currency.id)]
        ).unlink()
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.usd_currency.id,
                "rate": 1.5289,
                "create_date": "2010-01-01",
                "write_date": "2010-01-01",
            }
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
        # A fixed-price pricelist used as the partner's default pricelist. Its
        # ``discount_policy`` is left to the Odoo default on purpose.
        cls.sale_pricelist = cls._create_pricelist(
            "Test Sale pricelist", compute_price="fixed", value=60.00
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_product_pricelist": cls.sale_pricelist.id,
                "property_account_receivable_id": cls.a_receivable.id,
                "property_account_position_id": cls.fiscal_position.id,
            }
        )
        cls.sale_pricelist_fixed_without_discount = cls._create_pricelist(
            "Test Sale pricelist",
            compute_price="fixed",
            value=60.00,
            discount_policy="without_discount",
        )
        cls.sale_pricelist_with_discount = cls._create_pricelist(
            "Test Sale pricelist - 2",
            compute_price="percentage",
            value=10.0,
            discount_policy="with_discount",
        )
        cls.sale_pricelist_without_discount = cls._create_pricelist(
            "Test Sale pricelist - 3",
            compute_price="percentage",
            value=10.0,
            discount_policy="without_discount",
        )
        cls.sale_pricelist_with_discount_in_euros = cls._create_pricelist(
            "Test Sale pricelist - 4",
            compute_price="percentage",
            value=10.0,
            discount_policy="with_discount",
            currency=cls.euro_currency,
        )
        cls.sale_pricelist_without_discount_in_euros = cls._create_pricelist(
            "Test Sale pricelist - 5",
            compute_price="percentage",
            value=10.0,
            discount_policy="without_discount",
            currency=cls.euro_currency,
        )
        cls.sale_pricelist_fixed_with_discount_in_euros = cls._create_pricelist(
            "Test Sale pricelist - 6",
            compute_price="fixed",
            value=60.00,
            discount_policy="with_discount",
            currency=cls.euro_currency,
        )
        cls.sale_pricelist_fixed_wo_disc_euros = cls._create_pricelist(
            "Test Sale pricelist - 7",
            compute_price="fixed",
            value=60.00,
            discount_policy="without_discount",
            currency=cls.euro_currency,
        )
        cls.invoice = cls.AccountMove.create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.product_variant_ids[:1].id,
                            "name": "Test line",
                            "quantity": 1.0,
                            "price_unit": 100.00,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product.product_variant_ids[:2].id,
                            "name": "Test line 2",
                            "quantity": 1.0,
                            "price_unit": 100.00,
                        }
                    ),
                ],
            }
        )

    @classmethod
    def _create_pricelist(
        cls, name, *, compute_price, value, discount_policy=None, currency=None
    ):
        """
        Create a single-rule ``product.pricelist`` for ``cls.product``.
        ``value`` is interpreted as the fixed price for ``compute_price="fixed"``
        rules and as the discount percentage for ``compute_price="percentage"``
        rules.
        """
        item = {
            "applied_on": "1_product",
            "compute_price": compute_price,
            "product_tmpl_id": cls.product.id,
        }
        item["fixed_price" if compute_price == "fixed" else "percent_price"] = value
        vals = {"name": name, "item_ids": [Command.create(item)]}
        if discount_policy:
            vals["discount_policy"] = discount_policy
        if currency:
            vals["currency_id"] = currency.id
        return cls.ProductPricelist.create(vals)

    def _apply_pricelist(self, pricelist):
        """Set ``pricelist`` on the invoice, recompute prices and return line 1"""
        self.invoice.pricelist_id = pricelist.id
        self.invoice.button_update_prices_from_pricelist()
        return self.invoice.invoice_line_ids[:1]

    def test_account_invoice_pricelist(self):
        """The invoice inherits the partner's default pricelist"""
        self.assertEqual(self.invoice.pricelist_id, self.sale_pricelist)

    def test_account_invoice_change_pricelist(self):
        """Fixed price 60 fits in the 100 list price: applied as price, no discount"""
        invoice_line = self._apply_pricelist(self.sale_pricelist)
        self.assertEqual(invoice_line.price_unit, 60.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_pricelist_without_discount(self):
        """without_discount keeps list price 100 and books the 60 as a 40% discount"""
        invoice_line = self._apply_pricelist(self.sale_pricelist_fixed_without_discount)
        self.assertEqual(invoice_line.price_unit, 100.00)
        self.assertEqual(invoice_line.discount, 40.00)

    def test_account_invoice_with_discount_change_pricelist(self):
        """with_discount 10% off 100 yields a net price of 90, no discount shown"""
        invoice_line = self._apply_pricelist(self.sale_pricelist_with_discount)
        self.assertEqual(invoice_line.price_unit, 90.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_without_discount_change_pricelist(self):
        """without_discount 10% keeps price 100 and shows a 10% discount"""
        invoice_line = self._apply_pricelist(self.sale_pricelist_without_discount)
        self.assertEqual(invoice_line.price_unit, 100.00)
        self.assertEqual(invoice_line.discount, 10.00)

    def test_account_invoice_pricelist_with_discount_secondary_currency(self):
        """EUR with_discount 10%: 90 EUR converted to USD ~= 75.55, no discount"""
        invoice_line = self._apply_pricelist(self.sale_pricelist_with_discount_in_euros)
        self.assertAlmostEqual(invoice_line.price_unit, 75.55)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_pricelist_without_discount_secondary_currency(self):
        """EUR without_discount 10%: 100 EUR ~= 83.94 USD price, 10% discount"""
        invoice_line = self._apply_pricelist(
            self.sale_pricelist_without_discount_in_euros
        )
        self.assertAlmostEqual(invoice_line.price_unit, 83.94)
        self.assertEqual(invoice_line.discount, 10.00)

    def test_account_invoice_fixed_pricelist_with_discount_secondary_currency(self):
        """EUR fixed 60 with_discount: price kept at 60 in the invoice currency"""
        invoice_line = self._apply_pricelist(
            self.sale_pricelist_fixed_with_discount_in_euros
        )
        self.assertEqual(invoice_line.price_unit, 60.00)
        self.assertEqual(invoice_line.discount, 0.00)

    def test_account_invoice_fixed_pricelist_without_discount_secondary_currency(self):
        """EUR fixed 60 without_discount: 100 EUR ~= 83.94 USD, ~28.52% discount"""
        invoice_line = self._apply_pricelist(self.sale_pricelist_fixed_wo_disc_euros)
        self.assertAlmostEqual(invoice_line.price_unit, 83.94)
        self.assertAlmostEqual(invoice_line.discount, 28.52, places=2)

    def test_check_currency(self):
        # Assigning the EUR pricelist also switches the invoice to EUR, so there
        # is no conflict yet; forcing the currency back to USD is what must fail.
        self.invoice.with_context(force_check_currency=True).write(
            {"pricelist_id": self.sale_pricelist_with_discount_in_euros.id}
        )
        with self.assertRaises(UserError):
            self.invoice.with_context(force_check_currency=True).write(
                {"currency_id": self.usd_currency.id}
            )

    def test_account_invoice_with_discount_and_taxes(self):
        """Tax-included fixing keeps the 90 net price and no discount with taxes set"""
        tax = self.env["account.tax"].create(
            {
                "name": "Test Tax",
                "amount": 10.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        self.product.taxes_id = [Command.set([tax.id])]
        self.invoice.pricelist_id = self.sale_pricelist_with_discount.id
        for line in self.invoice.invoice_line_ids:
            line.tax_ids = [Command.set([tax.id])]
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.discount, 0.0)
        self.assertAlmostEqual(invoice_line.price_unit, 90.0)
