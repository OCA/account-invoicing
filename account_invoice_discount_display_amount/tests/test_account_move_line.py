# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestInvoiceDiscountDisplayCommon


class TestAccountMoveLine(TestInvoiceDiscountDisplayCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_check_line_setup(self):
        # check initial SetUp is Ok
        line1 = self.invoice.invoice_line_ids[0]

        result = self.obtain_attributes(line1)
        (
            taxes,
            tax_per_cent_amount,
            applied_discount_prior_taxes,
            applied_discount_with_taxes,
            without_discount_prior_taxes,
            without_discount_with_taxes,
        ) = result

        self.assertEqual(tax_per_cent_amount, 0.25)
        self.assertEqual(without_discount_prior_taxes, 1000)
        self.assertEqual(applied_discount_prior_taxes, 500)
        self.assertEqual(applied_discount_with_taxes, 625)
        self.assertEqual(without_discount_with_taxes, 1250)

    def test01_check_change_discount(self):
        # Change discount on the line. This will trigger a recompute
        line1 = self.invoice.invoice_line_ids[0]
        line1.discount = 25
        self.assertEqual(line1.price_total_no_discount, 1250)
        self.assertEqual(line1.discount_total, 312.5)

    def test02_check_change_tax(self):
        # Change tax on the line. This will trigger a recompute
        line1 = self.invoice.invoice_line_ids[0]
        line1.tax_ids = self.tax_15
        self.assertEqual(line1.price_total_no_discount, 1150)
        self.assertEqual(line1.discount_total, 575)

    def test03_check_change_quantity(self):
        # Change discount quantity the line. This will trigger a recompute
        line1 = self.invoice.invoice_line_ids[0]
        line1.quantity = 100
        self.assertEqual(line1.price_total_no_discount, 12500)
        self.assertEqual(line1.discount_total, 6250)

    def test04_check_change_unit_price(self):
        # Change discount oquantity the line. This will trigger a recompute
        line1 = self.invoice.invoice_line_ids[0]
        line1.price_unit = 1000
        self.assertEqual(line1.price_total_no_discount, 12500)
        self.assertEqual(line1.discount_total, 6250)
