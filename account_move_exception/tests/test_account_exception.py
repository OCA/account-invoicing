# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountException(TransactionCase):
    def setUp(self):
        super(TestAccountException, self).setUp()
        # Useful models
        self.AccountMove = self.env["account.move"].with_context(
            check_move_validity=False
        )
        self.AccountMoveLine = self.env["account.move.line"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_6")
        self.product_id_2 = self.env.ref("product.product_product_7")
        self.product_id_3 = self.env.ref("product.product_product_7")
        self.account_receivable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        self.account_exception_confirm = self.env["account.exception.confirm"]
        self.exception_noemail = self.env.ref(
            "account_move_exception.am_excep_no_email"
        )
        self.exception_qtycheck = self.env.ref(
            "account_move_exception.aml_excep_qty_check"
        )
        self.am_vals = {
            "move_type": "out_invoice",
            "partner_id": self.partner_id.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product_id_1.id,
                        "quantity": 5.0,
                        "price_unit": 500.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.product_id_2.id,
                        "quantity": 5.0,
                        "price_unit": 250.0,
                    },
                ),
            ],
        }

    def test_account_move_exception(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        self.am = self.AccountMove.create(self.am_vals.copy())

        self.assertEqual(self.am.state, "draft")
        # test all draft am
        self.am2 = self.AccountMove.create(self.am_vals.copy())

        self.AccountMove.test_all_draft_moves()
        self.assertEqual(self.am2.state, "draft")
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        self.am.ignore_exception = True
        self.am.action_post()
        self.assertEqual(self.am.state, "posted")

        # Add an account move to test after AM is confirmed
        # set ignore_exception = False  (Done by onchange of line_ids)
        field_onchange = self.AccountMove._onchange_spec()
        self.assertEqual(field_onchange.get("line_ids"), "1")
        self.env.cache.invalidate()
        self.am3New = self.AccountMove.new(self.am_vals.copy())
        self.am3New.ignore_exception = True
        self.am3New.state = "posted"
        self.am3New.onchange_ignore_exception()
        self.assertFalse(self.am3New.ignore_exception)
        self.am.line_ids.write(
            {
                "product_id": self.product_id_3.id,
                "quantity": 2,
                "price_unit": 30,
            }
        )

        # Set ignore exception True  (Done manually by user)
        self.am.ignore_exception = True
        self.am.button_cancel()
        self.am.button_draft()
        self.assertEqual(self.am.state, "draft")
        self.assertTrue(not self.am.ignore_exception)
        self.am.action_post()
        self.assertTrue(self.am.state, "posted")

        # Simulation the opening of the wizard account_exception_confirm and
        # set ignore_exception to True
        am_except_confirm = self.account_exception_confirm.with_context(
            **{
                "active_id": self.am.id,
                "active_ids": [self.am.id],
                "active_model": self.am._name,
            }
        ).create({"ignore": True})

        # avoid balance check:
        for line in self.am.line_ids:
            line.credit = 0.0

        am_except_confirm.action_confirm()
        self.assertTrue(self.am.ignore_exception)
