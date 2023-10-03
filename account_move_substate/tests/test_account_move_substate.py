# Copyright 2023 bosd (<bosd>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSubstate(TransactionCase):
    def setUp(self):
        super(TestBaseSubstate, self).setUp()
        self.substate_test_account_move = self.env["account.move"]
        self.substate_test_account_move_line = self.env["account.move.line"]

        self.substate_to_verify = self.env.ref(
            "account_move_substate.base_substate_to_verify_account_move"
        )
        self.substate_checked = self.env.ref(
            "account_move_substate.base_substate_checked_account_move"
        )
        self.substate_verified = self.env.ref(
            "account_move_substate.base_substate_verified_account_move"
        )

        self.product = self.env["product.product"].create({"name": "Test"})

    def test_account_move_substate(self):
        partner = self.env.ref("base.res_partner_12")
        invoice_test1 = self.substate_test_account_move.create(
            {
                # "name": "Test base substate to basic invoice",
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "quantity": 1,
                            "price_unit": 450,
                            "tax_ids": [(6, 0, [])],
                        },
                    )
                ],
            }
        )

        self.assertTrue(invoice_test1.state == "draft")

        with self.assertRaises(ValidationError):
            invoice_test1.substate_id = self.substate_verified
        # post the invoice
        invoice_test1.action_post()
        self.assertTrue(invoice_test1.substate_id == self.substate_verified)

        # test that there is no substate id
        invoice_test1.button_cancel()
        self.assertTrue(invoice_test1.state == "cancel")
        self.assertTrue(not invoice_test1.substate_id)
