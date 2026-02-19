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
        product_vals = {"name": "Product", "type": "service"}
        if "purchase_line_warn" in cls.env["product.template"]._fields:
            product_vals["purchase_line_warn"] = "no-message"
        if "sale_line_warn" in cls.env["product.template"]._fields:
            product_vals["sale_line_warn"] = "no-message"
        cls.product = cls.env["product.product"].create(product_vals)
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.company = cls.env.ref("base.main_company")
