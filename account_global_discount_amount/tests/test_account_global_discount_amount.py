# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import CommonGlobalDiscount


class TestAccountGlobalDiscountAmount(CommonGlobalDiscount):
    @classmethod
    def _create_invoice(cls, lines, discount_amount):
        # lines should be in the format [(price_unit, qty, tax, discount)]
        inv_lines = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "price_unit": price,
                    "quantity": qty,
                    "tax_ids": [(6, 0, tax.ids)],
                    "discount": discount_percent,
                },
            )
            for price, qty, tax, discount_percent in lines
        ]
        return cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": inv_lines,
                "global_discount_amount": discount_amount,
            }
        )

    def _check_discount_line(self, invoice, expected):
        lines = [
            (line.tax_ids, line.price_unit)
            for line in invoice.invoice_line_ids
            if line.is_discount_line
        ]
        lines.sort(key=lambda s: s[0].id)
        expected.sort(key=lambda s: s[0].id)
        self.assertEqual(lines, expected)
        self.assertTrue(invoice.global_discount_ok)

    def test_invoice_tax_exc(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 10)
        self.assertEqual(invoice.global_discount_base_on, "tax_exc")
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )
        self.assertEqual(invoice.amount_untaxed, 30)
        self.assertEqual(invoice.amount_total, 35.25)

    def test_invoice_tax_inc(self):
        self.vat20.price_include = True
        self.vat10.price_include = True
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 10)
        self.assertEqual(invoice.global_discount_base_on, "tax_inc")
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )
        self.assertEqual(invoice.amount_total, 30)
        self.assertEqual(invoice.amount_untaxed, 25.57)

    def test_invoice_no_tax(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.env["account.tax"], 0),
        ]
        invoice = self._create_invoice(lines, 10)
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -7.5),
                (self.env["account.tax"], -2.5),
            ],
        )
        self.assertEqual(invoice.amount_untaxed, 30)
        self.assertEqual(invoice.amount_total, 34.5)

    def test_invoice_with_percent_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 2, self.vat20, 50),
            (10, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 10)
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -5),
                (self.vat10, -5),
            ],
        )

    def test_invoice_multi_lines(self):
        lines = [
            # price, qty, vat, discount
            (10, 2, self.vat20, 0),
            (10, 1, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 10)
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )

    def test_invoice_remove_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 10)
        invoice.global_discount_amount = 0
        self._check_discount_line(invoice, [])
        self.assertEqual(invoice.amount_untaxed, 40)

    def test_invoice_add_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 0)
        invoice.global_discount_amount = 10
        self.assertEqual(invoice.amount_untaxed, 30)
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )

    def test_invoice_copy(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 10)
        new = invoice.copy()
        self._check_discount_line(
            new,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )
        self.assertEqual(invoice.amount_untaxed, 30)
        self.assertEqual(invoice.amount_total, 35.25)

    def test_invoice_rounding_issue(self):
        lines = [
            # price, qty, vat, discount
            (9.66, 1, self.vat20, 0),
            (5.98, 1, self.vat10, 0),
        ]
        invoice = self._create_invoice(lines, 0.51)
        self.assertEqual(invoice.amount_untaxed, 15.13)  # 9.66+5.98-0.52 = 15.13
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -0.31),
                (self.vat10, -0.20),
            ],
        )

    def test_invoice_rounding_issue_line_order(self):
        lines = [
            # price, qty, vat, discount
            (5.98, 1, self.vat10, 0),
            (9.66, 1, self.vat20, 0),
        ]
        invoice = self._create_invoice(lines, 0.51)
        self.assertEqual(invoice.amount_untaxed, 15.13)  # 9.66+5.98-0.52 = 15.13
        self._check_discount_line(
            invoice,
            [
                (self.vat20, -0.31),
                (self.vat10, -0.20),
            ],
        )
