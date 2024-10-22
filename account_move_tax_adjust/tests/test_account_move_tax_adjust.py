# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.tests.common import Form, TransactionCase


class TestAccountMoveTaxAdjust(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Account = cls.env["account.account"]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountTax = cls.env["account.tax"]
        cls.AccountType = cls.env["account.account.type"]
        cls.Partner = cls.env["res.partner"]
        cls.Journal = cls.env["account.journal"]

        cls.partner = cls.Partner.create({"name": "test"})
        cls.tax = cls.AccountTax.create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "amount": 15.0,
                "country_id": cls.env.ref("base.us").id,
            }
        )
        cls.account_type = cls.AccountType.create(
            {"name": "Test", "type": "receivable", "internal_group": "income"}
        )
        cls.account = cls.Account.create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.journal = cls.Journal.search([("type", "=", "sale")], limit=1)

    def create_simple_invoice(self, amount):
        invoice_form = Form(
            self.AccountMove.with_context(
                default_move_type="out_invoice",
                default_journal_id=self.journal.id,
            )
        )
        invoice_form.partner_id = self.partner

        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "Line 1"
            line_form.quantity = 1
            line_form.price_unit = amount
            line_form.tax_ids.clear()
            line_form.tax_ids.add(self.tax)

        invoice = invoice_form.save()
        return invoice

    def test_01_account_move_tax_adjust(self):
        """Tests tax adjustment in invoice form"""
        invoice = self.create_simple_invoice(100)
        json_vals = json.loads(invoice.tax_totals_json)
        # Check amount_total
        self.assertEqual(invoice.amount_untaxed, 100)
        self.assertEqual(invoice.amount_tax, 15)
        self.assertEqual(invoice.amount_total, 115.0)
        # Adjust tax from 15.0 to 10.0, diff = 5.0
        json_vals["groups_by_subtotal"]["Untaxed Amount"][0]["tax_group_amount"] = 10.0
        with Form(invoice) as inv:
            inv.tax_totals_json = json.dumps(json_vals)
        inv.save()
        self.assertEqual(invoice.amount_tax, 10.0)
