# Copyright 2024 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, TransactionCase


class TestBaseSubstate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.billing_model = cls.env["account.billing"]

        cls.partner = cls.env.ref("base.res_partner_12")
        cls.substate_to_verify = cls.env.ref(
            "account_billing_substate.base_substate_to_verify_account_billing"
        )
        cls.substate_checked = cls.env.ref(
            "account_billing_substate.base_substate_checked_account_billing"
        )

    def test_account_billing_substate(self):
        with Form(self.billing_model) as b:
            b.partner_id = self.partner
        billing = b.save()
        self.assertTrue(billing.billing_line_ids)
        self.assertEqual(billing.state, "draft")
        self.assertEqual(billing.substate_id, self.substate_to_verify)
        # Change substate to checked
        billing.substate_id = self.substate_checked.id
        self.assertEqual(billing.substate_id, self.substate_checked)
