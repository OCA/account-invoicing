# Copyright 2026 ACSONE SA/NV,BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceTaxAllowedAccountPrefix(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.env.company
        cls.country = cls.company.account_fiscal_country_id
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.account_60 = cls._create_account("601000X", "expense")
        cls.account_61 = cls._create_account("611000X", "expense")
        cls.account_2 = cls._create_account("240000X", "asset_fixed")
        cls.tax_no_prefix = cls._create_tax_with_prefix(21)
        cls.tax_60 = cls._create_tax_with_prefix(21, "60")
        cls.tax_61 = cls._create_tax_with_prefix(21, "61")
        cls.tax_2 = cls._create_tax_with_prefix(21, "2")
        cls.tax_sale_60 = cls._create_tax_with_prefix(21, "60", type_tax_use="sale")
        # multi-prefix taxes
        cls.tax_60_61 = cls._create_tax_with_prefix(21, "60,61")
        cls.tax_60_61_spaced = cls._create_tax_with_prefix(21, " 60, 61 ")
        cls.tax_2_60 = cls._create_tax_with_prefix(21, "2,60")

    @classmethod
    def _create_account(cls, code, acc_type):
        return cls.env["account.account"].create(
            {"name": "account", "code": code, "account_type": acc_type}
        )

    @classmethod
    def _create_tax_with_prefix(cls, amount, prefix="", type_tax_use="purchase"):
        tax = cls._create_tax("Tax No Prefix", amount, type_tax_use=type_tax_use)
        tax.allowed_account_prefix = prefix
        return tax

    def test_filter_allowed_for_account_without_prefix(self):
        """a tax without allowed prefix should always be allowed"""
        taxes = self.tax_no_prefix | self.tax_60 | self.tax_61
        allowed_taxes = taxes._filter_allowed_for_account(self.account_60)
        self.assertIn(self.tax_no_prefix, allowed_taxes)

    def test_filter_allowed_for_account_matching_prefix(self):
        """a tax should be allowed when the account code matches its prefix"""
        taxes = self.tax_60 | self.tax_61 | self.tax_2
        allowed_taxes = taxes._filter_allowed_for_account(self.account_60)
        self.assertIn(self.tax_60, allowed_taxes)
        self.assertNotIn(self.tax_61, allowed_taxes)
        self.assertNotIn(self.tax_2, allowed_taxes)

    def test_filter_allowed_for_account_non_matching_prefix(self):
        """a tax should be excluded when the account code does not match."""
        taxes = self.tax_60 | self.tax_61 | self.tax_2
        allowed_taxes = taxes._filter_allowed_for_account(self.account_2)
        self.assertIn(self.tax_2, allowed_taxes)
        self.assertNotIn(self.tax_60, allowed_taxes)
        self.assertNotIn(self.tax_61, allowed_taxes)

    def test_filter_allowed_for_account_multiple_prefixes(self):
        # a multi-prefix tax should match when the account matches the first prefix
        allowed_taxes = self.tax_60_61._filter_allowed_for_account(self.account_60)
        self.assertIn(self.tax_60_61, allowed_taxes)
        # a multi-prefix tax should match when the account matches the second prefix
        allowed_taxes = self.tax_60_61._filter_allowed_for_account(self.account_61)
        self.assertIn(self.tax_60_61, allowed_taxes)
        # spaces around comma-separated prefixes should be ignored
        taxes = self.tax_60_61_spaced | self.tax_2
        allowed_taxes = taxes._filter_allowed_for_account(self.account_61)
        self.assertIn(self.tax_60_61_spaced, allowed_taxes)
        self.assertNotIn(self.tax_2, allowed_taxes)

    def test_filter_allowed_for_account_without_prefix_strict(self):
        """without prefix, the tax should be excluded in strict mode"""
        allowed_taxes = self.tax_no_prefix._filter_allowed_for_account(
            self.account_60, strict=True
        )
        self.assertNotIn(self.tax_no_prefix, allowed_taxes)

    def test_tax_domain_without_account(self):
        """without account, tax_domain should fallback to the standard domain"""
        invoice = self.env["account.move"].new(
            {"move_type": "in_invoice", "partner_id": self.partner.id}
        )
        line = self.env["account.move.line"].new({"move_id": invoice.id})
        line.account_id = False
        self.assertEqual(
            line.tax_domain,
            [
                ("type_tax_use", "=?", invoice.invoice_filter_type_domain),
                ("company_id", "=", invoice.company_id.id),
                ("country_id", "=", invoice.tax_country_id.id),
            ],
        )

    def test_tax_domain_with_matching_prefix(self):
        """tax_domain should only keep taxes compatible with the account prefix"""
        invoice = self.env["account.move"].new(
            {"move_type": "in_invoice", "partner_id": self.partner.id}
        )
        line = self.env["account.move.line"].new(
            {"move_id": invoice.id, "account_id": self.account_60.id}
        )
        allowed_taxes = self.env["account.tax"].search(line.tax_domain)
        self.assertIn(self.tax_no_prefix, allowed_taxes)
        self.assertIn(self.tax_60, allowed_taxes)
        self.assertNotIn(self.tax_61, allowed_taxes)
        self.assertNotIn(self.tax_2, allowed_taxes)

    def test_tax_domain_with_multiple_prefixes(self):
        """tax_domain should keep taxes matching any configured prefix"""
        invoice = self.env["account.move"].new(
            {"move_type": "in_invoice", "partner_id": self.partner.id}
        )
        line = self.env["account.move.line"].new(
            {"move_id": invoice.id, "account_id": self.account_61.id}
        )
        allowed_taxes = self.env["account.tax"].search(line.tax_domain)
        self.assertIn(self.tax_61, allowed_taxes)
        self.assertIn(self.tax_60_61, allowed_taxes)
        self.assertIn(self.tax_60_61_spaced, allowed_taxes)
        self.assertNotIn(self.tax_2, allowed_taxes)

    def test_tax_domain_excludes_sale_taxes(self):
        """tax_domain should keep the standard purchase tax usage restriction"""
        invoice = self.env["account.move"].new(
            {"move_type": "in_invoice", "partner_id": self.partner.id}
        )
        line = self.env["account.move.line"].new(
            {"move_id": invoice.id, "account_id": self.account_60.id}
        )
        line.account_id = self.account_60.id
        allowed_taxes = self.env["account.tax"].search(line.tax_domain)
        self.assertIn(self.tax_60, allowed_taxes)
        self.assertNotIn(self.tax_sale_60, allowed_taxes)

    def test_tax_domain_updates_with_account_change(self):
        """tax_domain should be recomputed when account changes"""
        invoice = self.env["account.move"].new(
            {"move_type": "in_invoice", "partner_id": self.partner.id}
        )
        line = self.env["account.move.line"].new(
            {"move_id": invoice.id, "account_id": self.account_60.id}
        )
        allowed_taxes = self.env["account.tax"].search(line.tax_domain)
        self.assertIn(self.tax_60, allowed_taxes)
        self.assertIn(self.tax_60_61, allowed_taxes)
        self.assertNotIn(self.tax_61, allowed_taxes)

        line.account_id = self.account_61
        allowed_taxes = self.env["account.tax"].search(line.tax_domain)
        self.assertIn(self.tax_61, allowed_taxes)
        self.assertIn(self.tax_60_61, allowed_taxes)
        self.assertNotIn(self.tax_60, allowed_taxes)
