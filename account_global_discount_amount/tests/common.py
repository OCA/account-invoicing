# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class CommonGlobalDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.consu_delivery_01")
        cls.partner = cls.env["res.partner"].create({"name": "Partner Test"})

        type_current_liability = cls.env.ref(
            "account.data_account_type_current_liabilities"
        )

        output_vat10_acct = cls.env["account.account"].create(
            {"name": "10", "code": "10", "user_type_id": type_current_liability.id}
        )
        output_vat20_acct = cls.env["account.account"].create(
            {"name": "20", "code": "20", "user_type_id": type_current_liability.id}
        )

        # ==== Journals ====
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )

        # ==== Taxes ====
        tax_group_vat10 = cls.env["account.tax.group"].create({"name": "VAT10"})
        tax_group_vat20 = cls.env["account.tax.group"].create({"name": "VAT20"})
        cls.vat10 = cls.env["account.tax"].create(
            {
                "name": "TEST 10%",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 10.00,
                "tax_group_id": tax_group_vat10.id,
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100.0, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": output_vat10_acct.id,
                        },
                    ),
                ],
            }
        )
        cls.vat20 = cls.env["account.tax"].create(
            {
                "name": "TEST 20%",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 20.00,
                "tax_group_id": tax_group_vat20.id,
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100.0, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": output_vat20_acct.id,
                        },
                    ),
                ],
            }
        )


class CommonCaseGlobalDiscount:
    @classmethod
    def _create_record(cls, lines, discount_amount):
        raise NotImplementedError

    def _check_invoice_discount_line(self, invoice, expected):
        lines = [
            (line.tax_ids, line.price_unit)
            for line in invoice.invoice_line_ids
            if line.is_discount_line
        ]
        lines.sort(key=lambda s: s[0].id)
        expected.sort(key=lambda s: s[0].id)
        self.assertEqual(lines, expected)
        self.assertTrue(invoice.global_discount_ok)

    def _check_discount_line(self, record, expected):
        raise NotImplementedError

    def test_tax_exc(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        self.assertEqual(record.global_discount_base_on, "tax_exc")
        self._check_discount_line(
            record,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )
        self.assertEqual(record.amount_untaxed, 30)
        self.assertEqual(record.amount_total, 35.25)

    def test_tax_inc(self):
        self.vat20.price_include = True
        self.vat10.price_include = True
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        self.assertEqual(record.global_discount_base_on, "tax_inc")
        self._check_discount_line(
            record,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )
        self.assertEqual(record.amount_total, 30)
        self.assertEqual(record.amount_untaxed, 25.57)

    def test_no_tax(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.env["account.tax"], 0),
        ]
        record = self._create_record(lines, 10)
        self._check_discount_line(
            record,
            [
                (self.vat20, -7.5),
                (self.env["account.tax"], -2.5),
            ],
        )
        self.assertEqual(record.amount_untaxed, 30)
        self.assertEqual(record.amount_total, 34.5)

    def test_with_percent_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 2, self.vat20, 50),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        self._check_discount_line(
            record,
            [
                (self.vat20, -5),
                (self.vat10, -5),
            ],
        )

    def test_multi_lines(self):
        lines = [
            # price, qty, vat, discount
            (10, 2, self.vat20, 0),
            (10, 1, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        self._check_discount_line(
            record,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )

    def test_remove_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        record.global_discount_amount = 0
        self._check_discount_line(record, [])
        self.assertEqual(record.amount_untaxed, 40)

    def test_add_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 0)
        record.global_discount_amount = 10
        self.assertEqual(record.amount_untaxed, 30)
        self._check_discount_line(
            record,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )

    def test_copy(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        new = record.copy()
        self._check_discount_line(
            new,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )
        self.assertEqual(record.amount_untaxed, 30)
        self.assertEqual(record.amount_total, 35.25)

    def test_rounding_issue(self):
        lines = [
            # price, qty, vat, discount
            (9.66, 1, self.vat20, 0),
            (5.98, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 0.51)
        self.assertEqual(record.amount_untaxed, 15.13)  # 9.66+5.98-0.52 = 15.13
        self._check_discount_line(
            record,
            [
                (self.vat20, -0.31),
                (self.vat10, -0.20),
            ],
        )

    def test_rounding_issue_line_order(self):
        lines = [
            # price, qty, vat, discount
            (5.98, 1, self.vat10, 0),
            (9.66, 1, self.vat20, 0),
        ]
        record = self._create_record(lines, 0.51)
        self.assertEqual(record.amount_untaxed, 15.13)  # 9.66+5.98-0.52 = 15.13
        self._check_discount_line(
            record,
            [
                (self.vat20, -0.31),
                (self.vat10, -0.20),
            ],
        )
