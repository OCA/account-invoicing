from odoo.tests.common import TransactionCase


class TestInvoiceDiscountDisplayCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.account_invoice = cls.env["account.move"]
        cls.account_journal = cls.env["account.journal"]
        cls.journal = cls.account_journal.create(
            {"code": "test", "name": "test", "type": "sale"}
        )
        cls.partner = cls.env.ref("base.res_partner_3")

        cls.account_account = cls.env["account.account"]
        cls.account_rec1_id = cls.account_account.create(
            dict(
                code="20000",
                name="customer account",
                account_type="asset_receivable",
                reconcile=True,
            )
        )
        cls.product_product = cls.env["product.product"]
        cls.product = cls.product_product.create(
            {
                "name": "Test",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "list_price": 100,
                "type": "service",
            }
        )
        cls.tax_tax = cls.env["account.tax"]
        cls.tax_25 = cls.tax_tax.create(
            {
                "amount": 25,
                "amount_type": "percent",
                "name": "Tax 25%",
            }
        )
        cls.tax_15 = cls.tax_tax.create(
            {
                "amount": 15,
                "amount_type": "percent",
                "name": "Tax 15%",
            }
        )
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
                    "name": "product 1",
                    "price_unit": 100.00,
                    "tax_ids": cls.tax_25,
                    "discount": 50,
                },
            )
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

    def return_taxes(self):
        return self.tax_ids.compute_all(
            self.price_unit,
            self.move_id.currency_id,
            self.quantity,
            product=self.product_id,
            partner=self.partner_id,
        )

    @classmethod
    def obtain_attributes(cls, line):
        taxes = cls.return_taxes(line)
        tax_per_cent_amount = (line.tax_ids.amount) / 100
        line_applied_discount_prior_taxes = line.price_subtotal
        line_applied_discount_with_taxes = line.price_total
        line_without_discount_prior_taxes = taxes["total_excluded"]
        line_without_discount_with_taxes = taxes["total_included"]
        return (
            taxes,
            tax_per_cent_amount,
            line_applied_discount_prior_taxes,
            line_applied_discount_with_taxes,
            line_without_discount_prior_taxes,
            line_without_discount_with_taxes,
        )
