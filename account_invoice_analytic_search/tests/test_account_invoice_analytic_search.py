# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
import uuid
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestAccountMove(TransactionCase):
    def setUp(self):
        super().setUp()
        self.account_invoice = self.env["account.move"]
        self.account_model = self.env["account.account"]
        self.account_invoice_line = self.env["account.move.line"]
        self.analytic_model = self.env["account.analytic.account"]
        self.partner_2 = self.env.ref("base.res_partner_2").id
        self.product_4 = self.env.ref("product.product_product_4").id
        self.invoice_line_account = self._create_expense_account().id
        self.plan = self.env["account.analytic.plan"].create(
            {"name": "Test Plan", "company_id": self.env.company.id}
        )
        self.distribution_account = self.analytic_model.create(
            {
                "name": "Distribution Account",
                "code": "DA",
                "plan_id": self.plan.id,
                "company_id": self.env.company.id,
            }
        )
        self.has_legacy = "analytic_account_id" in self.account_invoice_line._fields
        self.legacy_account = (
            self.analytic_model.create(
                {
                    "name": "Legacy Account",
                    "code": "LA",
                    "plan_id": self.plan.id,
                    "company_id": self.env.company.id,
                }
            )
            if self.has_legacy
            else False
        )
        self.invoice_distribution = self._create_invoice(
            self.distribution_account, use_distribution=True
        )
        self.invoice_legacy = (
            self._create_invoice(self.legacy_account, use_distribution=False)
            if self.has_legacy
            else False
        )

    def _create_invoice(self, analytic_account, use_distribution):
        invoice = self.account_invoice.create(
            {
                "partner_id": self.partner_2,
                "move_type": "in_invoice",
            }
        )
        line_vals = {
            "product_id": self.product_4,
            "quantity": 1.0,
            "debit": 0.0,
            "credit": 0.0,
            "move_id": invoice.id,
            "name": "line",
            "account_id": self.invoice_line_account,
        }
        if use_distribution:
            line_vals["analytic_distribution"] = {str(analytic_account.id): 100}
        else:
            line_vals["analytic_account_id"] = analytic_account.id
        self.account_invoice_line.create(line_vals)
        return invoice

    def test_search_analytic_accounts_distribution(self):
        invoices = self.account_invoice.search(
            [("analytic_account_ids", "in", self.distribution_account.ids)]
        )
        self.assertIn(self.invoice_distribution, invoices)
        self.assertIn(
            self.distribution_account, self.invoice_distribution.analytic_account_ids
        )

    def test_search_analytic_accounts_legacy(self):
        if not self.has_legacy:
            self.skipTest("Legacy analytic account field not available")
        invoices = self.account_invoice.search(
            [("analytic_account_ids", "in", self.legacy_account.ids)]
        )
        self.assertIn(self.invoice_legacy, invoices)
        self.assertIn(self.legacy_account, self.invoice_legacy.analytic_account_ids)

    def test_get_analytic_account_depends(self):
        depends = self.account_invoice._get_analytic_account_depends()
        self.assertIn("invoice_line_ids", depends)
        if "analytic_distribution" in self.account_invoice_line._fields:
            self.assertIn("invoice_line_ids.analytic_distribution", depends)
        if self.has_legacy:
            self.assertIn("invoice_line_ids.analytic_account_id", depends)

    def test_get_analytic_account_depends_forced_fields(self):
        line_model = self.account_invoice_line
        dummy_field = line_model._fields["move_id"]
        with patch.dict(
            line_model._fields,
            {
                "analytic_distribution": dummy_field,
                "analytic_account_id": dummy_field,
            },
            clear=False,
        ):
            depends = self.account_invoice._get_analytic_account_depends()
        self.assertIn("invoice_line_ids.analytic_distribution", depends)
        self.assertIn("invoice_line_ids.analytic_account_id", depends)

    def test_compute_analytic_accounts_legacy_branch(self):
        if not self.has_legacy:
            self.skipTest("Legacy analytic account field not available")
        self.invoice_legacy._compute_analytic_accounts()
        self.assertIn(self.legacy_account, self.invoice_legacy.analytic_account_ids)

    def test_extract_distribution_from_string_values(self):
        distribution_payload = json.dumps(
            {
                str(self.distribution_account.id): {
                    "account_id": self.distribution_account.id
                },
                "extra": {
                    "analytic_account_id": self.distribution_account.id,
                },
                "": 100,
                "42-misc": 50,
                "12:extra": 75,
            }
        )
        line = type("DummyLine", (), {"analytic_distribution": distribution_payload})()
        account_ids = self.account_invoice._extract_distribution_account_ids(line)
        self.assertIn(self.distribution_account.id, account_ids)
        self.assertIn(42, account_ids)
        self.assertIn(12, account_ids)

    def test_extract_distribution_invalid_string(self):
        line = type("DummyLine", (), {"analytic_distribution": "not a json"})()
        account_ids = self.account_invoice._extract_distribution_account_ids(line)
        self.assertFalse(account_ids)

    def test_extract_distribution_from_dict_values(self):
        distribution_payload = {
            str(self.distribution_account.id): {
                "analytic_account_id": self.distribution_account.id
            },
            "77": {"account_id": 77},
            "100": {"analytic_account_id": "100"},
        }
        line = type("DummyLine", (), {"analytic_distribution": distribution_payload})()
        account_ids = self.account_invoice._extract_distribution_account_ids(line)
        self.assertIn(self.distribution_account.id, account_ids)
        self.assertIn(77, account_ids)
        self.assertIn(100, account_ids)

    def test_extract_distribution_non_dict_payload(self):
        line = type("DummyLine", (), {"analytic_distribution": [("foo", 99)]})()
        account_ids = self.account_invoice._extract_distribution_account_ids(line)
        self.assertFalse(account_ids)

    def test_compute_analytic_accounts_with_forced_fields(self):
        line_model = self.account_invoice_line
        dummy_field = line_model._fields["move_id"]
        legacy_account = self.analytic_model.create(
            {
                "name": "Patched Legacy Account",
                "code": "PLA",
                "plan_id": self.plan.id,
                "company_id": self.env.company.id,
            }
        )
        original_mapped = type(self.invoice_distribution).mapped

        def fake_mapped(records, expression, *args, **kwargs):
            if expression == "invoice_line_ids.analytic_account_id":
                return legacy_account
            return original_mapped(records, expression, *args, **kwargs)

        with patch.dict(
            line_model._fields,
            {
                "analytic_distribution": dummy_field,
                "analytic_account_id": dummy_field,
            },
            clear=False,
        ), patch.object(type(self.invoice_distribution), "mapped", fake_mapped):
            self.invoice_distribution._compute_analytic_accounts()

        self.assertIn(legacy_account, self.invoice_distribution.analytic_account_ids)
        self.assertIn(
            self.distribution_account, self.invoice_distribution.analytic_account_ids
        )

    def _create_expense_account(self):
        return self.account_model.create(
            {
                "name": "Expense Account",
                "code": "EXP%s" % uuid.uuid4().hex[:6],
                "account_type": "expense",
                "company_id": self.env.company.id,
            }
        )
