# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestInvoiceFixedDiscount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.user.groups_id |= cls.env.ref("account.group_account_invoice")
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env.ref("product.product_product_3")
        cls.account = cls.env["account.account"].search(
            [("account_type", "=", "income")],
            limit=1,
        )
        cls.output_vat_acct = cls.env["account.account"].create(
            {"name": "10", "code": "10", "account_type": "liability_current"}
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
        cls.invoice = cls._create_invoice()

    @classmethod
    def _create_invoice(cls, discount=0.00, discount_fixed=0.00):
        invoice_vals = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "quantity": 1.0,
                    "account_id": cls.account.id,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    "discount_fixed": discount_fixed,
                    "discount": discount,
                    "tax_ids": [(6, 0, [cls.vat.id])],
                },
            )
        ]
        invoice = (
            cls.env["account.move"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "journal_id": cls.env["account.journal"]
                    .search([("type", "=", "sale")], limit=1)
                    .id,
                    "partner_id": cls.partner.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": invoice_vals,
                }
            )
        )
        return invoice

    def test_01_discounts_fixed_single_unit(self):
        """Tests multiple discounts in line with taxes."""

        # Fixed discount 1.0 unit at 57.00
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                line.discount_fixed = 57.00

        # compute discount (57 / 200) * 100
        self.assertEqual(self.invoice.invoice_line_ids.discount, 28.5)
        # compute amount total (200 - 57) * 10%
        self.assertEqual(self.invoice.amount_total, 157.3)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 200.00)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 143.00)

        # Reset to regular discount at 20.00%
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                # Force the fixed discount as the onchange does not
                # handle the context properly
                line.discount_fixed = 0.0
                line.discount = 20.0

        self.assertEqual(self.invoice.invoice_line_ids.discount_fixed, 0.0)
        self.assertEqual(self.invoice.invoice_line_ids.discount, 20.0)
        self.assertEqual(self.invoice.amount_total, 176.0)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 200.00)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 160.00)

    def test_02_discounts_fixed_multiple_units(self):
        """Tests multiple discounts in line with taxes."""

        # Fixed discount 2.0 units at 50.00
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                line.discount_fixed = 25.00
                line.quantity = 2.0

        # compute discount ((50 / 2) / 200) * 100
        self.assertEqual(self.invoice.invoice_line_ids.discount, 12.5)
        self.assertEqual(self.invoice.amount_total, 385.0)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 200.00)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 350)

    def test_03_discount_fixed_no_tax(self):
        """Tests fixed discount with no taxes."""

        # Fixed discount 1.0 unit at 57.00
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                line.tax_ids.clear()
                line.discount_fixed = 57.00

        # compute discount (57 / 200) * 100
        self.assertEqual(self.invoice.invoice_line_ids.discount, 28.5)
        self.assertEqual(self.invoice.amount_total, 143)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 200.00)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 143)

    def test_03_discount_fixed_no_unit_prise(self):
        """Tests fixed discount with no taxes."""

        # Fixed discount 1.0 unit at 57.00
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                line.price_unit = 0.00
                line.discount_fixed = 57.00

        # compute discount (57 / 200) * 100
        self.assertEqual(self.invoice.invoice_line_ids.discount, 0.0)
        self.assertEqual(self.invoice.amount_total, 0)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 0.00)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 0)

    def test_04_base_line_set_to_none(self):
        self.vat._prepare_base_line_for_taxes_computation(
            None,
            price_unit=10,
            currency=1,
        )
