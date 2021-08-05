# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.tests import Form, common


class TestAccountMove(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.account_tax = cls.env["account.tax"].create(
            {"name": "0%", "amount_type": "fixed", "type_tax_use": "sale", "amount": 0}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner test"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "list_price": 10,
                "taxes_id": [(6, 0, [cls.account_tax.id])],
            }
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "TEST",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.other_account = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "ACC",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_other_income"
                ).id,
                "reconcile": True,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test sale journal", "type": "sale", "code": "TEST-SALE"}
        )
        cls.pricelist_usd = cls.env["product.pricelist"].create(
            {"name": "Pricelist USD", "currency_id": cls.currency_usd.id}
        )
        cls.pricelist_eur = cls.env["product.pricelist"].create(
            {"name": "Pricelist EUR", "currency_id": cls.currency_eur.id}
        )
        # Create custom rates to USD + EUR
        cls._create_currency_rate(cls, cls.currency_usd, "2000-01-01", 1.0)
        cls._create_currency_rate(cls, cls.currency_eur, "2000-01-01", 2.0)

    def _create_currency_rate(self, currency_id, name, rate):
        self.env["res.currency.rate"].create(
            {"currency_id": currency_id.id, "name": name, "rate": rate}
        )

    def _create_invoice(self, currency_id):
        move_form = Form(
            self.env["account.move"].with_context(default_type="out_invoice")
        )
        move_form.partner_id = self.partner
        move_form.journal_id = self.journal
        move_form.invoice_date = fields.Date.from_string("2000-01-01")
        move_form.currency_id = currency_id
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
        invoice = move_form.save()
        invoice.action_post()
        return invoice

    def test_01_invoice_usd(self):
        self.partner.property_product_pricelist = self.pricelist_usd
        invoice = self._create_invoice(self.currency_usd)
        self.assertEqual(invoice.currency_rate_amount, 1.0)

    def test_02_invoice_eur(self):
        self.partner.property_product_pricelist = self.pricelist_eur
        invoice = self._create_invoice(self.currency_eur)
        self.assertEqual(invoice.currency_rate_amount, 2.0)
        rate_custom = self.currency_eur.rate_ids.filtered(
            lambda x: x.name == fields.Date.from_string("2000-01-01")
        )
        rate_custom.rate = 3.0
        self.assertEqual(invoice.currency_rate_amount, 2.0)
        invoice.button_draft()
        self.assertEqual(invoice.currency_rate_amount, 3.0)
