from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestManualCurrency(TransactionCase):
    def setUp(self):
        super().setUp()
        self.usd = self.env.ref("base.USD")
        self.company = self.env.company
        self.partner = self.env["res.partner"].create({"name": "Codecov Smoke"})
        # 100 USD, manual rate 50 → 5 000 DOP expected
        income_account = self.env["account.account"].search(
            [("user_type_id.type", "=", "income")], limit=1
        )
        self.move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "currency_id": self.usd.id,
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Line",
                            "quantity": 1,
                            "price_unit": 100,
                            "account_id": income_account.id,
                        },
                    )
                ],
                "use_manual_rate": True,
                "manual_currency_rate": 50,
            }
        )

    def test_post_uses_manual_rate(self):
        """Posting must use 50 DOP/USD, not the daily rate."""
        self.move.action_post()
        pesos = sum(self.move.line_ids.filtered("debit").mapped("debit"))
        self.assertEqual(pesos, 5000.0)

    def test_get_rates_kwarg(self):
        """Patched _get_rates must ignore currency_table in 16.0."""
        # Must NOT raise TypeError
        self.usd._get_rates(self.company, fields.Date.today(), currency_table=None)
