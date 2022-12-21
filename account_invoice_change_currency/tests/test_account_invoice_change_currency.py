# Copyright 2018 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests import tagged
from odoo.tools import float_compare

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceChangeCurrency(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        decimal_precision_name = (
            cls.env["account.move.line"]._fields["price_unit"]._digits
        )
        decimal_precision = cls.env["decimal.precision"].search(
            [("name", "=", decimal_precision_name)]
        )
        cls.precision = decimal_precision.digits

    def test_change_invoice_currency(self):
        inv = self.init_invoice(
            "out_invoice",
            products=self.product_a + self.product_b,
            invoice_date=fields.Date.today(),
        )
        before_curr = inv.currency_id
        before_amount = inv.amount_total
        after_curr = self.env.ref("base.USD")
        inv.write({"currency_id": after_curr.id})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, after_curr, inv.company_id, fields.Date.today()
        )
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 0),
            0,
            "Total amount of invoice does not match to the expected value",
        )

    def test_change_validated_invoice_currency(self):
        inv = self.init_invoice(
            "out_invoice",
            products=self.product_a + self.product_b,
            invoice_date=fields.Date.today(),
        )
        before_amount = inv.amount_total
        inv.action_post()
        # Make sure that we can not change the currency after validated:
        inv.write({"currency_id": self.env.ref("base.USD").id})
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total,
            before_amount,
            "Total amount of invoice does not match to the expected value",
        )

    def test_create_invoice_update_currency(self):
        inv = self.init_invoice(
            "out_invoice",
            products=self.product_a + self.product_b,
            invoice_date=fields.Date.today(),
        )
        before_amount = inv.amount_total
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total,
            before_amount,
            "Amount must remain the same, because no currency changes",
        )

    def test_custom_rate_update_currency(self):
        inv = self.init_invoice(
            "out_invoice",
            products=self.product_a + self.product_b,
            invoice_date=fields.Date.today(),
        )
        before_amount = inv.amount_total
        self.assertEqual(inv.original_currency_id, self.env.ref("base.USD"))
        after_curr = self.env.ref("base.EUR")
        custom_rate = 1.13208
        inv.write({"currency_id": after_curr.id, "custom_rate": custom_rate})
        inv.write({"custom_rate": custom_rate})
        inv.action_account_change_currency()
        expected_value = before_amount * custom_rate
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, self.precision),
            0,
            "Total amount of invoice does not match to the expected value",
        )

    def test_custom_rate_zero_update_currency(self):
        inv = self.init_invoice(
            "out_invoice",
            products=self.product_a + self.product_b,
            invoice_date=fields.Date.today(),
        )
        before_amount = inv.amount_total
        before_curr = inv.currency_id
        custom_rate = 0.0
        usd = self.env.ref("base.USD")
        eur = self.env.ref("base.EUR")
        inv.write({"currency_id": usd.id, "custom_rate": custom_rate})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, usd, inv.company_id, fields.Date.today()
        )
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, self.precision),
            0,
            "Total amount of invoice does not match to the expected value",
        )
        # Change currency and set custom rate 0
        inv.write({"currency_id": eur.id, "custom_rate": custom_rate})
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total,
            before_amount,
            "Total amount of invoice does not match to the expected value",
        )
        # keep old_rate but now we update the currency.rate
        # (Original currency rate can not be changed anymore)
        before_amount = inv.amount_total
        old_rate = custom_rate
        new_rate = 1.6299
        usd_updated_rate = self.env["res.currency.rate"].create(
            {
                "name": fields.Date.today(),
                "rate": new_rate,
                "currency_id": usd.id,
                "company_id": inv.company_id.id,
            }
        )
        rate = usd_updated_rate.rate
        inv.write({"custom_rate": rate})
        inv.action_account_change_currency()
        expected_value = before_amount * rate
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 1),
            0,
            "Total amount of invoice does not match to the expected value",
        )
        # change custom rate then we trigger the conversion 2 times
        # The currency.rate modification above will be ignored and keep the
        # custom rate
        old_rate = inv.custom_rate
        inv.write({"currency_id": usd.id, "custom_rate": rate})
        inv.action_account_change_currency()
        before_amount = inv.amount_total
        rate = usd_updated_rate.rate
        inv.action_account_change_currency()
        expected_value = before_amount * rate / old_rate
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, self.precision),
            0,
            "Total amount of invoice does not match to the expected value",
        )
        before_amount = inv.amount_total
        rate = old_rate + 1
        inv.write({"custom_rate": rate})
        inv.action_account_change_currency()
        expected_value = before_amount
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 1),
            0,
            "Total amount of invoice does not match to the expected value",
        )
        inv.action_account_change_currency()
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 1),
            0,
            "Total amount of invoice does not match to the expected value",
        )

    def test_not_currency_change(self):
        inv = self.init_invoice(
            "out_invoice",
            products=self.product_a + self.product_b,
            invoice_date=fields.Date.today(),
        )
        before_amount = inv.amount_total
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total,
            before_amount,
            "Amount must remain the same, because None change was made",
        )

    def test_old_invoices(self):
        # This simulate an old invoice (no stored original values)
        inv = self.init_invoice(
            "out_invoice",
            products=self.product_a + self.product_b,
            invoice_date=fields.Date.today(),
        )
        inv.write({"original_currency_id": False})
        inv.invoice_line_ids.write({"original_price_unit": False})
        self.assertFalse(
            inv.original_currency_id,
            "There is an original currency in the invoice",
        )
        self.assertEqual(
            inv.invoice_line_ids.mapped("original_price_unit"),
            [0.0, 0.0],
            "There are original price units in the invoice",
        )
        # Now, trigger the action to store the original values to change currencies
        inv.action_account_change_currency()
        self.assertEqual(
            inv.original_currency_id,
            inv.currency_id,
            "Original currency of invoice is not match to the expected value",
        )
        self.assertEqual(
            inv.invoice_line_ids.mapped("original_price_unit"),
            inv.invoice_line_ids.mapped("price_unit"),
            "Original price units of invoice do not match to the expected value",
        )
