# Copyright 2023 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestAccountTaxOneVatCommon(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env.user.company_id = cls.company_data["company"]
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.vat_tax_1 = cls.env["account.tax"].create(
            {
                "name": "21%",
                "amount_type": "percent",
                "amount": 21,
                "sequence": 10,
                "is_vat": True,
            }
        )
        cls.vat_tax_2 = cls.env["account.tax"].create(
            {
                "name": "12%",
                "amount_type": "percent",
                "amount": 12,
                "sequence": 20,
                "is_vat": True,
            }
        )
        cls.tax_3 = cls.env["account.tax"].create(
            {
                "name": "6%",
                "amount_type": "percent",
                "amount": 6,
                "sequence": 30,
            }
        )
        cls.test_move = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "line_ids": [
                    (
                        0,
                        None,
                        {
                            "name": "revenue line 1",
                            "account_id": cls.company_data[
                                "default_account_revenue"
                            ].id,
                            "debit": 500.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "name": "counterpart line",
                            "account_id": cls.company_data[
                                "default_account_expense"
                            ].id,
                            "debit": 0.0,
                            "credit": 500.0,
                        },
                    ),
                ],
            }
        )
        cls.vat_taxes = cls.vat_tax_1 | cls.vat_tax_2
        cls.mixed_taxes = cls.vat_tax_1 | cls.tax_3
        cls.product_test = cls.env["product.product"].create(
            {
                "name": "product_test",
                "company_id": cls.env.user.company_id.id,
            }
        )

    def _create_invoice(self, taxes_per_line):
        """Create an invoice on the fly.

        :param taxes_per_line: A list of tuple (price_unit, account.tax recordset)
        """
        vals = {
            "move_type": "out_invoice",
            "partner_id": self.partner_a.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "xxxx",
                        "quantity": 1,
                        "price_unit": amount,
                        "tax_ids": [(6, 0, taxes.ids)],
                    },
                )
                for amount, taxes in taxes_per_line
            ],
        }
        return self.env["account.move"].create(vals)
