# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestAccountInvoiceCustomRoundingCommon(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_sale_a.write(
            {
                "amount": 21,
            }
        )
        cls.product_a.write({"name": "Product", "type": "service"})
        cls.partner_a.write({"name": "Partner"})
