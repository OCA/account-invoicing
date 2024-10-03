# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import common
from odoo.tests.common import tagged


@tagged("post_install", "-at_install")
class TestAccountTierValidation(common.TransactionCase):
    def test_01_tier_definition_models(self):
        res = self.env["tier.definition"]._get_tier_validation_model_names()
        self.assertIn("account.move", res)

    def test_02_form(self):
        for _type in ("in_invoice", "out_invoice", "in_refund", "out_refund"):
            self.env["tier.definition"].create(
                {
                    "model_id": self.env["ir.model"]
                    .search([("model", "=", "account.move")])
                    .id,
                    "definition_domain": "[('move_type', '=', '%s')]" % _type,
                }
            )
            with common.Form(
                self.env["account.move"].with_context(default_move_type=_type)
            ) as form:
                form.save()
                self.assertTrue(form.hide_post_button)
