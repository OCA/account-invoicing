# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestHrExpenseTierValidation(common.TransactionCase):
    def setUp(self):
        super(TestHrExpenseTierValidation, self).setUp()
        self.tier_definition = self.env['tier.definition']

    def test_get_tier_validation_model_names(self):
        self.assertIn('account.invoice',
                      self.tier_definition._get_tier_validation_model_names())
