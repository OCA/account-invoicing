# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestAccountInvoiceCustomRoundingCommon


class TestAccountInvoiceCustomRounding(TestAccountInvoiceCustomRoundingCommon):
    def create_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "company_id": self.company.id,
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product.id,
                            "quantity": 1.0,
                            "price_unit": 7757.68,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.product.id,
                            "quantity": 1.0,
                            "price_unit": 4710.88,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    ),
                ],
            }
        )
        return invoice

    def test_base_case_company_globally(self):
        self.company.write({"tax_calculation_rounding_method": "round_globally"})
        invoice = self.create_invoice()
        self.assertFalse(invoice.tax_calculation_rounding_method)
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertFalse(reverse_move.tax_calculation_rounding_method)
        self.assertAlmostEqual(reverse_move.amount_total, 15086.96, places=2)

    def test_base_case_company_per_line(self):
        self.company.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice = self.create_invoice()
        self.assertFalse(invoice.tax_calculation_rounding_method)
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertFalse(reverse_move.tax_calculation_rounding_method)
        self.assertAlmostEqual(reverse_move.amount_total, 15086.95, places=2)

    def test_custom_rounding_company_globally(self):
        self.company.write({"tax_calculation_rounding_method": "round_globally"})
        self.partner.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice = self.create_invoice()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_per_line")
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.write({"tax_calculation_rounding_method": False})
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_globally"})
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertEqual(reverse_move.tax_calculation_rounding_method, "round_globally")
        self.assertAlmostEqual(reverse_move.amount_total, 15086.96, places=2)

    def test_custom_rounding_company_per_line(self):
        self.company.write({"tax_calculation_rounding_method": "round_per_line"})
        self.partner.write({"tax_calculation_rounding_method": "round_globally"})
        invoice = self.create_invoice()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_globally")
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.write({"tax_calculation_rounding_method": False})
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_globally"})
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice._check_balanced()
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertEqual(reverse_move.tax_calculation_rounding_method, "round_per_line")
        self.assertAlmostEqual(reverse_move.amount_total, 15086.95, places=2)
