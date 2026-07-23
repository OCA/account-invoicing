# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestProductAveragePriceInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.today = fields.Date.context_today(cls.env["product.product"])

    def _create_invoice(
        self, move_type, product, quantity, price_unit, invoice_date, company=False
    ):
        invoice = self.init_invoice(
            move_type, products=product, invoice_date=invoice_date, company=company
        )
        invoice.invoice_line_ids.write(
            {
                "quantity": quantity,
                "price_unit": price_unit,
                "tax_ids": [Command.clear()],
            }
        )
        invoice.action_post()
        return invoice

    def test_stored_after_buttons_independent(self):
        product = self.product_a
        # Without invoices there's neither average nor period.
        product._update_avg_prices()
        self.assertEqual(product.avg_purchase_price, 0.0)
        self.assertFalse(product.avg_purchase_price_date_from)
        self.assertIn("No data", product.avg_purchase_price_period)
        self._create_invoice("in_invoice", product, 4.0, 25.0, self.today)
        self._create_invoice("out_invoice", product, 2.0, 50.0, self.today)
        # The purchase button only refreshes the purchase average.
        product.action_update_avg_purchase_price()
        self.assertEqual(product.avg_purchase_price, 25.0)
        self.assertEqual(product.avg_purchase_price_date_to, self.today)
        self.assertIn("From", product.avg_purchase_price_period)
        self.assertEqual(product.avg_sale_price, 0.0)
        # The sale button only refreshes the sale average.
        product.action_update_avg_sale_price()
        self.assertEqual(product.avg_sale_price, 50.0)
        self.assertEqual(product.avg_purchase_price, 25.0)

    def test_expanding_window(self):
        product = self.product_b
        # Bill dated 45 days ago -> not found within 30 days, found within 60.
        invoice_date = self.today - timedelta(days=45)
        self._create_invoice("in_invoice", product, 2.0, 30.0, invoice_date)
        product._update_avg_prices()
        self.assertEqual(product.avg_purchase_price, 30.0)
        self.assertEqual(
            product.avg_purchase_price_date_from, self.today - timedelta(days=60)
        )

    def test_company_dependent(self):
        product = self.product_a
        company_2 = self.company_data_2["company"]
        self._create_invoice("in_invoice", product, 4.0, 25.0, self.today)
        self._create_invoice(
            "in_invoice", product, 2.0, 40.0, self.today, company=company_2
        )
        self.env["product.product"]._cron_update_avg_prices()
        self.assertEqual(product.avg_purchase_price, 25.0)
        self.assertEqual(product.with_company(company_2).avg_purchase_price, 40.0)
        self.assertEqual(product.product_tmpl_id.avg_purchase_price, 25.0)
        self.assertEqual(
            product.product_tmpl_id.with_company(company_2).avg_purchase_price, 40.0
        )

    def test_template_level(self):
        product = self.product_a
        self._create_invoice("in_invoice", product, 4.0, 25.0, self.today)
        template = product.product_tmpl_id
        template.action_update_avg_purchase_price()
        self.assertEqual(template.avg_purchase_price, 25.0)
        # The button also refreshes the variant snapshot.
        self.assertEqual(product.avg_purchase_price, 25.0)
