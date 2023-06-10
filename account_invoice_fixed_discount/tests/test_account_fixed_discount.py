# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import TransactionCase


class TestInvoiceFixedDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceFixedDiscount, cls).setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test"})

        cls.product = cls.env.ref("product.product_product_3")
        if not cls.product:
            raise Exception("No product.product_product_3 found")

        account_type = cls.env.ref("account.data_account_type_revenue")
        if not account_type:
            raise Exception('No account type named "Revenue" found')

        cls.account = cls.env["account.account"].search(
            [("user_type_id", "=", account_type.id)], limit=1
        )
        if not cls.account:
            raise Exception('No account with user_type_id of type "Revenue" found')

        type_current_liability = cls.env.ref(
            "account.data_account_type_current_liabilities"
        )
        if not type_current_liability:
            raise Exception("No account.data_account_type_current_liabilities found")

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

        cls.tax_account_id = cls.env["account.account"].search(
            [("user_type_id", "=", account_type.id)], limit=1
        )
        if not cls.tax_account_id:
            raise Exception("No account with user_type_id of type 'Revenue' found")

        cls.product.taxes_id = [(6, 0, [cls.vat.id])]
        cls.invoice_vals = {
            "partner_id": cls.partner.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "account_id": cls.account.id,
                        "quantity": 1.0,
                        "price_unit": cls.product.list_price,
                        "discount_fixed": 10.0,
                    },
                )
            ],
        }
