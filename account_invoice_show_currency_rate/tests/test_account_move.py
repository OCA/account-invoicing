# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.tests import Form, common


class TestAccountMove(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        usd = cls.env.ref("base.USD")
        eur = cls.env.ref("base.EUR")
        cls.currency = cls.env.ref("base.main_company").currency_id
        cls.currency_extra = eur if cls.currency == usd else usd
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
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.other_account = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "ACC",
                "account_type": "income_other",
                "reconcile": True,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test sale journal", "type": "sale", "code": "TEST-SALE"}
        )
        # Purchase setup to reproduce the reset-to-draft rounding bug on a
        # multi-line foreign-currency vendor bill.
        cls.purchase_journal = cls.env["account.journal"].create(
            {"name": "Test purchase journal", "type": "purchase", "code": "TPUR"}
        )
        cls.pricelist_currency = cls.env["product.pricelist"].create(
            {"name": "Pricelist Currency", "currency_id": cls.currency.id}
        )
        cls.pricelist_currency_extra = cls.env["product.pricelist"].create(
            {"name": "Pricelist Currency Extra", "currency_id": cls.currency_extra.id}
        )
        # Create custom rates to currency + currency_extra
        cls._create_currency_rate(cls, cls.currency, "2000-01-01", 1.0)
        cls._create_currency_rate(cls, cls.currency_extra, "2000-01-01", 2.0)

    def _create_currency_rate(self, currency_id, name, rate):
        self.env["res.currency.rate"].create(
            {"currency_id": currency_id.id, "name": name, "rate": rate}
        )

    def _create_invoice(self, currency_id):
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.partner
        move_form.invoice_date = fields.Date.from_string("2000-01-01")
        move_form.currency_id = currency_id
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
        invoice = move_form.save()
        invoice.action_post()
        return invoice

    def test_01_invoice_currency(self):
        self.partner.property_product_pricelist = self.pricelist_currency
        invoice = self._create_invoice(self.currency)
        self.assertAlmostEqual(invoice.currency_rate_amount, 1.0, 2)
        self.assertAlmostEqual(invoice.line_ids[0].currency_rate, 1.0, 2)

    def test_02_invoice_currency_extra(self):
        self.partner.property_product_pricelist = self.pricelist_currency_extra
        invoice = self._create_invoice(self.currency_extra)
        self.assertAlmostEqual(invoice.currency_rate_amount, 2.0, 2)
        self.assertAlmostEqual(invoice.line_ids[0].currency_rate, 2.0, 2)
        rate_custom = self.currency_extra.rate_ids.filtered(
            lambda x: x.name == fields.Date.from_string("2000-01-01")
        )
        rate_custom.rate = 3.0
        self.assertAlmostEqual(invoice.currency_rate_amount, 2.0, 2)
        self.assertAlmostEqual(invoice.line_ids[0].currency_rate, 2.0, 2)
        invoice.button_draft()
        # The invoice was posted before, so the real booked rate (2.0) is kept
        # instead of falling back to the table rate (3.0). This prevents the
        # balance from being re-derived and wrongly unbalanced on reset to draft.
        self.assertAlmostEqual(invoice.currency_rate_amount, 2.0, 2)
        self.assertAlmostEqual(invoice.line_ids[0].currency_rate, 2.0, 2)

    def _create_vendor_bill_multi(self, currency_id, amounts):
        """Multi-line foreign-currency vendor bill, mirroring the production
        case where per-line rounding of the re-derived balance breaks
        _check_balanced on reset to draft."""
        move_form = Form(
            self.env["account.move"].with_context(
                default_move_type="in_invoice",
                default_journal_id=self.purchase_journal.id,
            )
        )
        move_form.partner_id = self.partner
        move_form.invoice_date = fields.Date.from_string("2000-01-01")
        move_form.currency_id = currency_id
        for amount in amounts:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product
                line_form.price_unit = amount
        invoice = move_form.save()
        invoice.action_post()
        return invoice

    def test_03_reset_to_draft_no_balance_error(self):
        """A multi-line foreign-currency vendor bill that was posted can be
        reset to draft without raising a false 'unbalanced entry' error, and
        keeping the booked balances (regression of the production case)."""
        # Rate where per-line rounding of these amounts breaks the balance when
        # the rate is re-applied uniformly on draft (reproduces the bug).
        rate_custom = self.currency_extra.rate_ids.filtered(
            lambda x: x.name == fields.Date.from_string("2000-01-01")
        )
        rate_custom.rate = 1.1777
        amounts = [
            21900,
            9750,
            20400,
            500,
            500,
            360,
            360,
            450,
            500,
            280,
            2625,
            2475,
            450,
        ]
        invoice = self._create_vendor_bill_multi(self.currency_extra, amounts)
        balances_posted = invoice.line_ids.mapped("balance")
        # Without the fix this raises UserError ("unbalanced entry"); with it,
        # the booked rate is kept and the entry stays balanced.
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(
            self.env.company.currency_id.round(sum(invoice.line_ids.mapped("balance"))),
            0.0,
        )
        self.assertEqual(invoice.line_ids.mapped("balance"), balances_posted)

    def test_04_reset_to_draft_edit_and_repost(self):
        """After reset to draft, the bill can be edited and posted again
        without the false unbalanced error (V3)."""
        rate_custom = self.currency_extra.rate_ids.filtered(
            lambda x: x.name == fields.Date.from_string("2000-01-01")
        )
        rate_custom.rate = 1.1777
        amounts = [
            21900,
            9750,
            20400,
            500,
            500,
            360,
            360,
            450,
            500,
            280,
            2625,
            2475,
            450,
        ]
        invoice = self._create_vendor_bill_multi(self.currency_extra, amounts)
        invoice.button_draft()
        invoice.invoice_line_ids[0].price_unit = 22000
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
