# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class NoAutofollowCommon(TransactionCase):
    def setUp(self, *args, **kwargs):
        """
        Test for orders, to check autofollow when the
        'customer no autofollow' mode is enabled in settings
        """
        super(NoAutofollowCommon, self).setUp(*args, **kwargs)

        self.partner1 = self.env["res.partner"].create(
            {"name": "Test1", "email": "test1@test.com"}
        )

        self.product1 = self.env["product.product"].create(
            {
                "name": "desktop",
                "uom_id": 1,
                "lst_price": 1000.0,
                "standard_price": 800.0,
                "taxes_id": [(6, 0, [])],
                "supplier_taxes_id": [(6, 0, [])],
            }
        )
