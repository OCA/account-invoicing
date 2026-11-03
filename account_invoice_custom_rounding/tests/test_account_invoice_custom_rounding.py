# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import tagged

from .common import TestAccountInvoiceCustomRoundingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceCustomRounding(TestAccountInvoiceCustomRoundingCommon):
    def create_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_a.id,
                            "quantity": 1.0,
                            "price_unit": 7757.68,
                            "tax_ids": [(6, 0, [self.tax_sale_a.id])],
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_a.id,
                            "quantity": 1.0,
                            "price_unit": 4710.88,
                            "tax_ids": [(6, 0, [self.tax_sale_a.id])],
                        },
                    ),
                ],
            }
        )
        return invoice

    def test_base_case_company_globally(self):
        self.env.company.write({"tax_calculation_rounding_method": "round_globally"})
        invoice = self.create_invoice()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_globally")
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertEqual(reverse_move.tax_calculation_rounding_method, "round_globally")
        self.assertAlmostEqual(reverse_move.amount_total, 15086.96, places=2)

    def test_base_case_company_per_line(self):
        self.env.company.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice = self.create_invoice()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_per_line")
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertEqual(reverse_move.tax_calculation_rounding_method, "round_per_line")
        self.assertAlmostEqual(reverse_move.amount_total, 15086.95, places=2)

    def test_custom_rounding_company_globally(self):
        self.env.company.write({"tax_calculation_rounding_method": "round_globally"})
        self.partner_a.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice = self.create_invoice()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_per_line")
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_globally"})
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_globally"})
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertEqual(reverse_move.tax_calculation_rounding_method, "round_globally")
        self.assertAlmostEqual(reverse_move.amount_total, 15086.96, places=2)

    def test_custom_rounding_company_per_line(self):
        self.env.company.write({"tax_calculation_rounding_method": "round_per_line"})
        self.partner_a.write({"tax_calculation_rounding_method": "round_globally"})
        invoice = self.create_invoice()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_globally")
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_globally"})
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)
        invoice.write({"tax_calculation_rounding_method": "round_per_line"})
        invoice._check_balanced({"records:": invoice})
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)
        invoice.action_post()
        reverse_move = invoice._reverse_moves()
        self.assertEqual(reverse_move.tax_calculation_rounding_method, "round_per_line")
        self.assertAlmostEqual(reverse_move.amount_total, 15086.95, places=2)
