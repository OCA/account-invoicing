# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestAccountMoveCancelConfirm(TransactionCase):
    def setUp(self):
        super().setUp()
        self.account_move_model = self.env["account.move"]
        self.register_payments_model = self.env["account.payment.register"]
        self.payment_model = self.env["account.payment"]
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_7")
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        # Add parameter with cancel confirm
        self.env["ir.config_parameter"].create(
            {"key": "account.move.cancel_confirm_disable", "value": "False"}
        )
        self.env["ir.config_parameter"].create(
            {"key": "account.payment.cancel_confirm_disable", "value": "False"}
        )
        self.journal_bank = self.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        self.move = self.account_move_model.create(
            {
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def test_01_cancel_move(self):
        """
        - Cancel a account move with the wizard asking for the reason
        - Then the account move should be canceled and the reason stored
        """
        # Click cancel, cancel confirm wizard will open. Type in cancel_reason
        res = self.move.button_cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "button_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(**ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.move.cancel_reason, wizard.cancel_reason)
        self.assertEqual(self.move.state, "cancel")
        # Set to draft
        self.move.button_draft()
        self.assertEqual(self.move.cancel_reason, False)
        self.assertEqual(self.move.state, "draft")

    def test_02_cancel_payment(self):
        """
        - Cancel a payment with the wizard asking for the reason
        - Then the payment should be canceled and the reason stored
        """
        # Create Payment
        self.move.action_post()
        res = self.move.action_register_payment()
        payment_register_form = Form(
            self.env[res["res_model"]].with_context(**res["context"])
        )
        payment = payment_register_form.save()
        payment.action_create_payments()
        payment = self.payment_model.search([], order="id desc", limit=1)
        self.assertEqual(payment.state, "paid")
        # Click cance, cancel confirm wizard will open. Type in cancel_reason
        res = payment.action_cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "action_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(**ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(payment.cancel_reason, wizard.cancel_reason)
        self.assertEqual(payment.state, "canceled")
        # Set to draft
        payment.action_draft()
        self.assertEqual(payment.cancel_reason, False)
        self.assertEqual(payment.state, "draft")
