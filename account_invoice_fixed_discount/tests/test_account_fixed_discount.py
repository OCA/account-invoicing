# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestInvoiceFixedDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceFixedDiscount, cls).setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env.ref("product.product_product_3")
        cls.account = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        type_current_liability = cls.env.ref(
            "account.data_account_type_current_liabilities"
        )
        cls.output_vat_acct = cls.env["account.account"].create(
            {"name": "10", "code": "10", "user_type_id": type_current_liability.id}
        )
        cls.tax_group_vat = cls.env["account.tax.group"].create({"name": "VAT"})
        cls.vat = cls.env["account.tax"].create(
            {
                "name": "TEST 10%",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 10.00,
                "tax_group_id": cls.tax_group_vat.id,
                "tax_exigibility": "on_invoice",
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100.0, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": cls.output_vat_acct.id,
                        },
                    ),
                ],
            }
        )

    def _create_invoice(self, discount=0.00, discount_fixed=0.00):
        invoice_vals = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "quantity": 1.0,
                    "account_id": self.account.id,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    "discount_fixed": discount_fixed,
                    "discount": discount,
                    "tax_ids": [(6, 0, [self.vat.id])],
                },
            )
        ]
        invoice = (
            self.env["account.move"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "journal_id": self.env["account.journal"]
                    .search([("type", "=", "sale")], limit=1)
                    .id,
                    "partner_id": self.partner.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": invoice_vals,
                }
            )
        )
        return invoice

    def test_01_discounts_fixed(self):
        """Tests multiple discounts in line with taxes."""
        invoice = self._create_invoice(discount_fixed=57)
        with self.assertRaises(ValidationError):
            invoice.invoice_line_ids.discount = 50
        invoice.invoice_line_ids._onchange_discount_fixed()
        self.assertEqual(invoice.invoice_line_ids.discount, 0.00)
        invoice.invoice_line_ids._onchange_price_subtotal()
        invoice.line_ids.write({"recompute_tax_line": True})
        invoice._onchange_invoice_line_ids()
        # compute amount total (200 - 57) * 10%
        self.assertEqual(invoice.amount_total, 157.3)
        self.assertEqual(invoice.invoice_line_ids.price_unit, 200.00)
        self.assertEqual(invoice.invoice_line_ids.price_subtotal, 143.00)

    def test_02_discounts(self):
        invoice = self._create_invoice(discount=50)
        invoice.invoice_line_ids._onchange_discount()
        self.assertEqual(invoice.invoice_line_ids.discount_fixed, 0.00)
        self.assertEqual(invoice.invoice_line_ids.price_unit, 200.00)
        self.assertEqual(invoice.invoice_line_ids.price_subtotal, 100.00)
