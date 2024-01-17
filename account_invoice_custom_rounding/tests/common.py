# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestAccountInvoiceCustomRoundingCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax",
                "amount_type": "percent",
                "amount": 21,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "service"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.company = cls.env.ref("base.main_company")
