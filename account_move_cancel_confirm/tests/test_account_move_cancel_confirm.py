# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestAccountMoveCancelConfirm(TransactionCase):
    def setUp(self):
        super().setUp()
        self.account_invoice_model = self.env["account.invoice"]
        self.register_payments_model = self.env["account.register.payments"]
        self.payment_model = self.env["account.payment"]
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_7")
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        # Add parameter with cancel confirm
        self.env["ir.config_parameter"].create(
            {"key": "account.invoice.cancel_confirm_disable", "value": "False"}
        )
        self.env["ir.config_parameter"].create(
            {"key": "account.move.cancel_confirm_disable", "value": "False"}
        )
        self.env["ir.config_parameter"].create(
            {"key": "account.payment.cancel_confirm_disable", "value": "False"}
        )
        self.journal_bank = self.env["account.journal"].create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BNK67",
                "update_posted": True
            }
        )
        self.income_account = self.env["account.account"].create({
            "code": "INC",
            "name": "revenue account",
            "user_type_id": self.env.ref("account.data_account_type_revenue").id,
        })
        self.invoice = self.account_invoice_model.create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.journal_bank.id,
                "date_invoice": fields.Date.today(),
                "type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "price_unit": 100.0,
                            "name": self.product.name,
                            "account_id": self.income_account.id
                        }
                    )
                ],
            }
        )

    def test_01_cancel_invoice(self):
        """
        - Cancel a account invoice with the wizard asking for the reason
        - Then the account invoice should be canceled and the reason stored
        """
        # Click cancel, cancel confirm wizard will open. Type in cancel_reason
        res = self.invoice.action_invoice_cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "action_invoice_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(**ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.invoice.cancel_reason, wizard.cancel_reason)
        self.assertEqual(self.invoice.state, "cancel")
        # Set to draft
        self.invoice.action_invoice_draft()
        self.assertEqual(self.invoice.cancel_reason, False)

    def test_02_cancel_payment(self):
        """
        - Cancel a payment with the wizard asking for the reason
        - Then the payment should be canceled and the reason stored
        """
        # Create Payment
        self.invoice.action_invoice_open()
        ctx = {
            "active_model": "account.invoice",
            "active_ids": [self.invoice.id],
        }
        register_payments = self.register_payments_model.with_context(
            ctx
        ).create({
            "journal_id": self.journal_bank.id,
            "payment_method_id": self.payment_method_manual_in.id,
        })
        register_payments.create_payments()
        payment = self.payment_model.search([], order="id desc", limit=1)
        self.assertEqual(payment.state, "posted")
        # Click cance, cancel confirm wizard will open. Type in cancel_reason
        res = payment.cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(**ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(payment.cancel_reason, wizard.cancel_reason)
        self.assertEqual(payment.state, "cancelled")
        # Set to draft
        payment.action_draft()
        self.assertEqual(payment.cancel_reason, False)
        self.assertEqual(payment.state, "draft")
