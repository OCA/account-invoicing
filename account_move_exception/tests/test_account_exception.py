# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.AccountMove = cls.env["account.move"].with_context(
            check_move_validity=False
        )
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.partner_id = cls.env.ref("base.res_partner_1")
        cls.product_id_1 = cls.env.ref("product.product_product_6")
        cls.product_id_2 = cls.env.ref("product.product_product_7")
        cls.product_id_3 = cls.env.ref("product.product_product_7")
        cls.account_receivable = cls.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                )
            ],
            limit=1,
        )
        cls.account_exception_confirm = cls.env["account.exception.confirm"]
        cls.exception_noemail = cls.env.ref("account_move_exception.am_excep_no_email")
        cls.exception_qtycheck = cls.env.ref(
            "account_move_exception.aml_excep_qty_check"
        )
        cls.am_vals = {
            "move_type": "out_invoice",
            "partner_id": cls.partner_id.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product_id_1.id,
                        "quantity": 5.0,
                        "price_unit": 500.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": cls.product_id_2.id,
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
        self.assertEqual(field_onchange.get("invoice_line_ids"), "1")
        self.am3New = self.AccountMove.new(self.am_vals.copy())
        self.am3New.ignore_exception = True
        self.am3New.state = "posted"
        self.am3New.onchange_ignore_exception()
        self.assertFalse(self.am3New.ignore_exception)
        self.am.invoice_line_ids.write(
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
