# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, TransactionCase


class TestAccountManualCurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inv_model = cls.env["account.move"]
        cls.payment_model = cls.env["account.payment"]
        cls.payment_register_model = cls.env["account.payment.register"]
        cls.register_view_id = "account.view_account_payment_register_form"
        # Activate Multi Currency
        cls.usd_currency = cls.env.ref("base.USD")
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.eur_currency.active = True

        cls.partner1 = cls.env.ref("base.res_partner_3")

        cls.cash = cls.env["account.journal"].create(
            {"name": "Cash Test", "type": "cash", "code": "CT"}
        )

    def _create_invoice(
        self,
        partner,
        invoice_type,
        currency,
        manual_currency=False,
        manual_currency_rate=0.0,
        type_currency="company_rate",
    ):
        inv_line = [
            Command.create(
                {
                    "product_id": self.env.ref("product.product_product_8").id,
                    "name": "Test Invoice Line",
                    "quantity": 1.0,
                    "price_unit": 100.0,
                },
            )
        ]
        invoice = self.inv_model.create(
            {
                "partner_id": partner.id,
                "invoice_date": fields.Date.today(),
                "move_type": invoice_type,
                "currency_id": currency.id,
                "manual_currency": manual_currency,
                "type_currency": type_currency,
                "manual_currency_rate": manual_currency_rate,
                "invoice_line_ids": inv_line,
            }
        )
        return invoice

    def test_01_account_move_inverse_currency(self):
        # Create invoice with custom rate: 10 USD = 1 EUR
        invoice1 = self._create_invoice(
            self.partner1,
            "in_invoice",
            self.eur_currency,
            True,
            10,
            "inverse_company_rate",
        )
        invoice1._fields_view_get()
        self.assertTrue(invoice1.is_manual)
        # Currency will recompute to default
        self.assertEqual(invoice1.manual_currency_rate, 10)
        invoice1.action_refresh_currency()
        self.assertNotEqual(invoice1.manual_currency_rate, 10)
        total_currency_not_manual = invoice1.total_company_currency
        self.assertAlmostEqual(
            total_currency_not_manual,
            sum(invoice1.line_ids.filtered(lambda l: l.product_id).mapped("balance")),
        )
        # Use manual currency
        with Form(invoice1) as inv:
            inv.manual_currency = True
            inv.type_currency = "inverse_company_rate"
            inv.manual_currency_rate = 20  # Convert rate: 20 USD = 1 EUR
        inv.save()
        # After manual currency, total currency will recompute
        self.assertNotEqual(invoice1.total_company_currency, total_currency_not_manual)
        self.assertAlmostEqual(
            invoice1.total_company_currency,
            sum(invoice1.line_ids.filtered(lambda l: l.product_id).mapped("balance")),
        )
        invoice1.action_post()
        self.assertEqual(invoice1.state, "posted")
        # Can't refresh rate when state is not draft
        with self.assertRaises(ValidationError):
            invoice1.action_refresh_currency()

        # Create invoice
        invoice2 = self._create_invoice(self.partner1, "in_invoice", self.usd_currency)
        invoice2.action_post()
        self.assertEqual(invoice2.state, "posted")

        # Register Payment
        # Can't register payment with not same manual currency
        ctx = {
            "active_ids": (invoice1 + invoice2).mapped("line_ids").ids,
            "active_model": "account.move.line",
        }
        with self.assertRaises(UserError):
            Form(
                self.payment_register_model.with_context(**ctx),
                view=self.register_view_id,
            ).save()
        ctx = {
            "active_ids": [invoice1.id],
            "active_model": "account.move",
        }
        with Form(
            self.payment_register_model.with_context(**ctx),
            view=self.register_view_id,
        ) as f:
            f.amount = invoice1.amount_total
        wiz = f.save()
        action_payment = wiz.action_create_payments()
        # Check move in payment must equal invoice
        payment = self.payment_model.browse(action_payment["res_id"])
        self.assertAlmostEqual(
            payment.move_id.total_company_currency, invoice1.total_company_currency
        )
