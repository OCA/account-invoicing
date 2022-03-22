# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import common
from odoo.tests.common import tagged

from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester


@tagged("post_install", "-at_install")
class TestAccountTierValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountTierValidation, cls).setUpClass()

        setup_test_model(cls.env, [TierValidationTester])

        cls.test_model = cls.env[TierValidationTester._name]

        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester")]
        )

        # Access record:
        cls.env["ir.model.access"].create(
            {
                "name": "access.tester",
                "model_id": cls.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )

        # Create users:
        group_ids = cls.env.ref("base.group_system").ids
        cls.test_user_1 = cls.env["res.users"].create(
            {"name": "John", "login": "test1", "groups_id": [(6, 0, group_ids)]}
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )

        cls.test_record = cls.test_model.create({"test_field": 2.5})

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, [TierValidationTester])
        return super(TestAccountTierValidation, cls).tearDownClass()

    def test_01_tier_definition_models(self):
        """When the user can validate all future reviews, it is not needed
        to request a validation, the action can be done straight forward."""
        res = self.tier_def_obj._get_tier_validation_model_names()
        self.assertIn("account.move", res)
