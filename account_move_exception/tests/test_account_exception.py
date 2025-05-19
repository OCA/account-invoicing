# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountException(TransactionCase):
    def setUp(self):
        super().setUp()
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
            [("account_type", "=", "asset_receivable")],
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

    def test_all_draft(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        am = self.AccountMove.create(self.am_vals.copy())
        am2 = self.AccountMove.create(self.am_vals.copy())
        self.assertEqual(am.state, "draft")
        self.assertEqual(am2.state, "draft")

        self.AccountMove.test_all_draft_moves()

    def test_post_if_ignore_exception(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        am = self.AccountMove.create(self.am_vals.copy())
        am.ignore_exception = True

        am.action_post()

        self.assertEqual(am.state, "posted")

    def test_onchange_ignore_exception(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        am3New = self.AccountMove.new(self.am_vals.copy())
        am3New.ignore_exception = True
        am3New.state = "posted"

        am3New.onchange_ignore_exception()

        self.assertFalse(am3New.ignore_exception)

    def test_cancel_draft(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        am = self.AccountMove.create(self.am_vals.copy())
        am.line_ids.write(
            {
                "product_id": self.product_id_3.id,
                "quantity": 2,
                "price_unit": 30,
            }
        )
        am.ignore_exception = True

        am.button_cancel()
        am.button_draft()
        self.assertEqual(am.state, "draft")
        self.assertFalse(am.ignore_exception)

    def test_wizard_account_exception_confirm(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        am = self.AccountMove.create(self.am_vals.copy())
        am.ignore_exception = True
        am.action_post()
        self.assertTrue(am.state, "posted")
        am_except_confirm = self.account_exception_confirm.with_context(
            **{
                "active_id": am.id,
                "active_ids": [am.id],
                "active_model": am._name,
            }
        ).create({"ignore": True})

        am_except_confirm.action_confirm()
        self.assertTrue(am.ignore_exception)
