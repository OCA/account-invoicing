# Copyright 2018 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common
from odoo import fields
from odoo.tools import float_compare


class TestAccountInvoiceChangeCurrency(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.precision = self.env["decimal.precision"].precision_get("Payment Terms")
        res_users_account_manager = self.env.ref("account.group_account_manager")
        self.manager = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                dict(
                    name="Adviser",
                    company_id=self.env.ref("base.main_company").id,
                    login="fm",
                    email="accountmanager@yourcompany.com",
                    groups_id=[(6, 0, [res_users_account_manager.id])],
                )
            )
        )

        # Needed to create invoice
        self.account_type = self.env["account.account.type"].create(
            {
                "name": "acc type test 2",
                "type": "other",
                "include_initial_balance": True,
                "internal_group": "asset",
            }
        )
        self.account_account_line = self.env["account.account"].create(
            {
                "name": "acc inv line test",
                "code": "X2021",
                "user_type_id": self.account_type.id,
                "reconcile": True,
            }
        )
        self.product_1 = self.env["product.product"].create({"name": "Product 1"})
        self.product_2 = self.env["product.product"].create({"name": "Product 2"})
        self.analytic_account = self.env["account.analytic.account"].create(
            {"name": "test account"}
        )
        self.tax_account = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_current_assets").id,
                )
            ],
            limit=1,
        )

    def create_simple_invoice(self, date=False, context=None, inv_type=None):
        if not context:
            context = {}
        context["default_move_type"] = True
        invoice_lines = [
            (
                0,
                0,
                {
                    "product_id": self.product_1.id,
                    "quantity": 5.0,
                    "price_unit": 142.0,
                    "name": "Product that cost 142",
                    "account_id": self.account_account_line.id,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": self.product_2.id,
                    "quantity": 4.0,
                    "price_unit": 213.0,
                    "name": "Product that cost 213",
                    "account_id": self.account_account_line.id,
                },
            ),
        ]
        invoice = (
            self.env["account.move"]
            .with_user(self.manager)
            .with_context(**context)
            .create(
                {
                    "partner_id": 1,
                    "move_type": inv_type or "in_invoice",
                    "invoice_date": date,
                    "currency_id": self.env.ref("base.EUR").id,
                    "invoice_line_ids": invoice_lines,
                    "state": "draft",
                }
            )
        )
        return invoice

    def test_change_invoice_currency(self):
        inv = self.create_simple_invoice(fields.Date.today())
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
        inv = self.create_simple_invoice(fields.Date.today())
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
        inv = self.create_simple_invoice()
        before_amount = inv.amount_total
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total,
            before_amount,
            "Amount must remain the same, because no currency changes",
        )

    def test_custom_rate_update_currency(self):
        inv = self.create_simple_invoice(fields.Date.today())
        before_amount = inv.amount_total
        after_curr = self.env.ref("base.USD")
        custom_rate = 1.13208
        inv.write({"currency_id": after_curr.id, "custom_rate": custom_rate})
        inv.write({"custom_rate": custom_rate})
        inv.action_account_change_currency()
        expected_value = before_amount * custom_rate
        # TODO: Check float comparation, 12013.64 vs 12013.632959999999
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, self.precision),
            1,
            "Total amount of invoice does not match to the expected value",
        )

    def test_custom_rate_zero_update_currency(self):
        inv = self.create_simple_invoice()
        before_amount = inv.amount_total
        before_curr = inv.currency_id
        custom_rate = 0.0
        usd = self.env.ref("base.USD")
        eur = self.env.ref("base.EUR")
        inv.write({"currency_id": usd.id, "custom_rate": custom_rate})
        inv.write({"custom_rate": custom_rate})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, usd, inv.company_id, fields.Date.today()
        )
        # Comparison 2004.64 vs 2004.67
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 0),
            0,
            "Total amount of invoice does not match to the expected value",
        )
        # Change currency and set custom rate 0
        inv.write({"currency_id": eur.id, "custom_rate": custom_rate})
        inv.write({"custom_rate": custom_rate})
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total,
            before_amount,
            "Total amount of invoice does not match to the expected value",
        )
        # Change Again custom rate with old_rate but now without new currency
        inv.write({"custom_rate": custom_rate})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, eur, inv.company_id, fields.Date.today()
        )
        self.assertEqual(
            inv.amount_total,
            expected_value,
            "Total amount of invoice does not match to the expected value",
        )
        # Custom rate with 0 but now without new currency
        inv.write({"custom_rate": custom_rate})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, eur, inv.company_id, fields.Date.today()
        )
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
        expected_value = before_amount
        # TODO: Check float comparation, 1562.0 vs 1562.0
        self.assertEqual(
            inv.amount_total,
            expected_value,
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
        expected_value = before_amount * rate / old_rate
        # TODO: Check float comparation, 4107.93 vs 4107.946074605804
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 1),
            0,
            "Total amount of invoice does not match to the expected value",
        )
        inv.action_account_change_currency()
        # TODO: Check float comparation, 4107.93 vs 4107.946074605804
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 1),
            0,
            "Total amount of invoice does not match to the expected value",
        )
        # Test if there are no currency
        inv.write({"currency_id": False})
        self.assertEqual(
            inv.custom_rate,
            1.0,
            "Custom rate of invoice does not match to the expected value",
        )

    def test_not_currency_change(self):
        inv = self.create_simple_invoice(inv_type="out_invoice")
        before_amount = inv.amount_total
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total,
            before_amount,
            "Amount must remain the same, because None change was made",
        )

    def test_old_invoices(self):
        # This simulate an old invoice (no stored original values)
        inv = self.create_simple_invoice(fields.Date.today())
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
