# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestAccountInvoiceTierValidation(common.TransactionCase):
    def setUp(self):
        super(TestAccountInvoiceTierValidation, self).setUp()

        # common models
        self.account_invoice = self.env["account.invoice"]
        self.tier_definition = self.env["tier.definition"]

    def test_get_under_validation_exceptions(self):
        self.assertIn(
            "route_id", self.account_invoice._get_under_validation_exceptions()
        )

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "account.invoice",
            self.tier_definition._get_tier_validation_model_names(),
        )
