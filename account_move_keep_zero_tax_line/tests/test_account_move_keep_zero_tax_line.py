# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveKeepZeroTaxLine(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.tax_sale_a_zero = cls.company_data["default_tax_sale"]
        cls.tax_sale_a_zero.amount = 0.0
        cls.tax_purchase_a_zero = cls.company_data["default_tax_purchase"]
        cls.tax_purchase_a_zero.amount = 0.0

    def test_01_no_config_zero_tax_line(self):
        """Test tax0% standard without config"""
        self.assertFalse(self.company_data["company"].tax_zero_line)

        purchase_move = self.init_invoice(
            "in_invoice",
            self.partner_a,
            "2024-01-01",
            amounts=[1000],
            taxes=self.tax_purchase_a_zero,
            post=True,
        )
        self.assertEqual(len(purchase_move.line_ids), 2)  # without line tax 0.0

        sale_move = self.init_invoice(
            "out_invoice",
            self.partner_a,
            "2024-01-01",
            amounts=[1000],
            taxes=self.tax_sale_a_zero,
            post=True,
        )
        self.assertEqual(len(sale_move.line_ids), 2)  # without line tax 0.0

    def test_02_config_zero_tax_line_purchase(self):
        """Test vendor bill, tax0% with config"""
        self.assertFalse(self.company_data["company"].tax_zero_line)
        self.company_data["company"].tax_zero_line = True
        self.assertTrue(self.company_data["company"].tax_zero_line)

        purchase_move = self.init_invoice(
            "in_invoice",
            self.partner_a,
            "2024-01-01",
            amounts=[1000],
            taxes=self.tax_purchase_a_zero,
            post=True,
        )
        self.assertEqual(len(purchase_move.line_ids), 3)  # with line tax 0.0

    def test_03_config_zero_tax_line_sale(self):
        """Test customer invoice, tax0% with config"""
        self.assertFalse(self.company_data["company"].tax_zero_line)
        self.company_data["company"].tax_zero_line = True
        self.assertTrue(self.company_data["company"].tax_zero_line)

        sale_move = self.init_invoice(
            "out_invoice",
            self.partner_a,
            "2024-01-01",
            amounts=[1000],
            taxes=self.tax_sale_a_zero,
            post=True,
        )
        self.assertEqual(len(sale_move.line_ids), 3)  # with line tax 0.0
