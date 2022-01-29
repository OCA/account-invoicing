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
