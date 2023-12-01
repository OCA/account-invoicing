from .common import TestInvoiceDiscountDisplayCommon


class TestAccountMoveLine(TestInvoiceDiscountDisplayCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Add some more lines
        invoice_line_data = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "quantity": 10.0,
                    "account_id": cls.account_account.search(
                        [
                            (
                                "account_type",
                                "=",
                                "income",
                            )
                        ],
                        limit=1,
                    ).id,
                    "name": "product line 1",
                    "price_unit": 100.00,
                    "tax_ids": cls.tax_25,
                    "discount": 50,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "quantity": 1.0,
                    "account_id": cls.account_account.search(
                        [
                            (
                                "account_type",
                                "=",
                                "income",
                            )
                        ],
                        limit=1,
                    ).id,
                    "name": "product line 2",
                    "price_unit": 1000.00,
                    "tax_ids": cls.tax_15,
                    "discount": 40,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "quantity": 5.0,
                    "account_id": cls.account_account.search(
                        [
                            (
                                "account_type",
                                "=",
                                "income",
                            )
                        ],
                        limit=1,
                    ).id,
                    "name": "product line 3",
                    "price_unit": 20.00,
                    "tax_ids": cls.tax_25,
                    "discount": 50,
                },
            ),
        ]

        cls.invoice = cls.account_invoice.create(
            dict(
                name="Test Customer Invoice",
                journal_id=cls.journal.id,
                partner_id=cls.partner.id,
                invoice_line_ids=invoice_line_data,
                move_type="out_invoice",
            )
        )

    def test06_check_invoice_setup(self):
        # check initial SetUp is Ok
        invoice = self.invoice

        self.assertEqual(invoice.discount_total, 1147.5)
        self.assertEqual(invoice.price_total_no_discount, 2525)

    def test07_check_invoice_when_lines_change(self):
        # Producing a recompute of discount_total/price_total_no_discount
        # on each of the lines in order to cause a recompute of the invoice's
        # own discount_total/price_total_no_discount attributes.
        invoice = self.invoice

        line1 = invoice.invoice_line_ids[0]
        line2 = invoice.invoice_line_ids[1]
        line3 = invoice.invoice_line_ids[2]

        line1.price_unit = 75
        line2.tax_ids = self.tax_25
        line3.quantity = 16

        self.assertEqual(invoice.price_total_no_discount, 2587.5)
        self.assertEqual(invoice.discount_total, 1168.75)
