# Copyright 2026 Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveLine(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "lst_price": 100.0,
                "taxes_id": False,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "tax_ids": False,
                        }
                    )
                ],
            }
        )
        cls.line = cls.invoice.invoice_line_ids

    def test_aggregated_discount_from_distribution(self):
        self.line.discount_distribution = [10, 5]
        self.assertAlmostEqual(self.line.discount, 14.5, places=4)

    def test_aggregated_discount_zero_when_distribution_cleared(self):
        self.line.discount_distribution = [10, 5]
        self.line.discount_distribution = []
        self.assertEqual(self.line.discount, 0.0)

    def test_subtotal_uses_aggregated_discount(self):
        self.line.discount_distribution = [10, 5]
        self.assertAlmostEqual(self.line.price_subtotal, 85.5, places=2)

    def test_inverse_writes_distribution_when_empty(self):
        self.assertFalse(self.line.discount_distribution)
        self.line.discount = 10
        self.assertEqual(self.line.discount_distribution, [10])
        self.assertAlmostEqual(self.line.discount, 10.0, places=4)

    def test_inverse_overwrites_single_element_distribution(self):
        self.line.discount_distribution = [10]
        self.line.discount = 25
        self.assertEqual(self.line.discount_distribution, [25])
        self.assertAlmostEqual(self.line.discount, 25.0, places=4)

    def test_inverse_overwrites_multi_element_distribution(self):
        self.line.discount_distribution = [10, 5]
        # A direct write on the aggregated field always realigns the
        # distribution to a single element so the two fields never drift apart.
        self.line.write({"discount": 99})
        self.assertEqual(self.line.discount_distribution, [99])
        self.assertAlmostEqual(self.line.discount, 99.0, places=4)

    def test_inverse_with_zero_clears_distribution(self):
        self.line.discount_distribution = [10]
        self.line.discount = 0
        self.assertFalse(self.line.discount_distribution)
        self.assertEqual(self.line.discount, 0.0)

    def test_distribution_persists_across_reload(self):
        self.line.discount_distribution = [10, 5, 2]
        self.line.flush_recordset()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.discount_distribution, [10, 5, 2])
