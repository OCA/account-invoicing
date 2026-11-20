# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import Command
from odoo.tests import Form, new_test_user

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestAccountInvoiceRefundReason(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.invoice_refund_obj = cls.env["account.move.reversal"]
        cls.reason_obj = cls.env["account.move.refund.reason"]

        cls.reason_id = cls.env["account.move.refund.reason"].create(
            {"name": "Cancellation"}
        )
        cls.other_reason_id = cls.env["account.move.refund.reason"].create(
            {"name": "Wrong Price"}
        )

        cls.account_invoice_customer0 = cls.init_invoice(
            "out_invoice",
            products=cls.product_a + cls.product_b,
        )

    def create_refund(self, active_ids=None, refund_method="refund", **values):
        """Helper function to create a refund wizard"""

        if not active_ids:
            active_ids = self.account_invoice_customer0.ids

        create_values = dict(
            date=datetime.date.today(),
            reason_id=self.reason_id.id,
            journal_id=self.account_invoice_customer0.journal_id.id,
        )
        create_values.update(**values)

        move_reversal = self.invoice_refund_obj.with_context(
            active_model="account.move",
            active_ids=active_ids,
        ).create(create_values)
        self.move_reversal = move_reversal

        previous = move_reversal.move_ids.reversal_move_ids
        if refund_method == "refund":
            move_reversal.refund_moves()
        else:
            move_reversal.modify_moves()
        account_invoice_refund = move_reversal.move_ids.reversal_move_ids - previous

        self.assertEqual(
            move_reversal.reason,
            account_invoice_refund.reason_id.name,
        )
        return account_invoice_refund

    def test_onchange_reason_id(self):
        self.account_invoice_customer0.action_post()
        account_invoice_refund_0 = self.create_refund()
        reversal_move = self.account_invoice_customer0.reversal_move_ids
        self.assertEqual(
            set(account_invoice_refund_0.ids),
            set(reversal_move.ids),
        )
        self.assertEqual(
            reversal_move.reason_id.id,
            self.reason_id.id,
        )

    def test_invoice_with_several_refunds(self):
        self.account_invoice_customer0.action_post()
        account_invoice_refund_0 = self.create_refund()
        self.assertEqual(
            account_invoice_refund_0.reason_id.id,
            self.reason_id.id,
        )

        account_invoice_refund_1 = self.create_refund(reason_id=self.other_reason_id.id)
        self.assertEqual(
            account_invoice_refund_1.reason_id.id,
            self.other_reason_id.id,
        )

        reversal_moves = self.account_invoice_customer0.reversal_move_ids
        self.assertEqual(
            set(reversal_moves.ids),
            set([account_invoice_refund_0.id, account_invoice_refund_1.id]),
        )

    def test_invoice_refund_modify(self):
        self.account_invoice_customer0.action_post()
        account_invoice_refund_0 = self.create_refund(
            refund_method="modify",
        )
        self.assertEqual(
            account_invoice_refund_0.reason_id.id,
            self.reason_id.id,
        )
        new_invoice = self.move_reversal.new_move_ids
        self.assertEqual(new_invoice.move_type, "out_invoice")
        self.assertFalse(new_invoice.reason_id)

    def test_previous_refund_without_reason_untouched(self):
        self.account_invoice_customer0.action_post()
        old_refund = self.create_refund(reason_id=False)
        new_refund = self.create_refund()
        self.assertFalse(old_refund.reason_id)
        self.assertEqual(new_refund.reason_id, self.reason_id)

    def test_invoice_refund_several_invoices(self):
        account_invoice_customer1 = self.init_invoice(
            "out_invoice",
            partner=self.partner_b,
            products=self.product_a + self.product_b,
        )
        self.account_invoice_customer0.action_post()
        account_invoice_customer1.action_post()
        account_invoice_refunds = self.create_refund(
            active_ids=[
                self.account_invoice_customer0.id,
                account_invoice_customer1.id,
            ],
        )
        reversal_move0 = self.account_invoice_customer0.reversal_move_ids
        reversal_move1 = account_invoice_customer1.reversal_move_ids
        self.assertEqual(
            set(account_invoice_refunds.ids),
            set([reversal_move0.id, reversal_move1.id]),
        )
        self.assertEqual(
            reversal_move0.reason_id.id,
            self.reason_id.id,
        )

        self.assertEqual(
            reversal_move1.reason_id.id,
            self.reason_id.id,
        )

    def test_reason_shown_empty_on_credit_notes_and_reversals(self):
        for move_type, shown in (
            ("out_refund", True),
            ("in_refund", True),
            ("out_invoice", False),
            ("in_invoice", False),
        ):
            with self.subTest(move_type=move_type):
                move = self.env["account.move"].create(
                    {"move_type": move_type, "partner_id": self.partner_a.id}
                )
                invisible = Form(move)._get_modifier("reason_id", "invisible")
                self.assertEqual(not invisible, shown)

        for refund_type in ("out_refund", "in_refund"):
            with self.subTest(reversal_of=refund_type):
                refund = self.init_invoice(
                    refund_type, products=self.product_a, post=True
                )
                reversal = refund._reverse_moves()
                self.assertFalse(reversal.reason_id)
                invisible = Form(reversal)._get_modifier("reason_id", "invisible")
                self.assertFalse(invisible)

    def test_reason_editable(self):
        billing_user = new_test_user(
            self.env,
            login="billing_user",
            groups="account.group_account_invoice",
            company_id=self.env.company.id,
            company_ids=[Command.set(self.env.company.ids)],
        )
        refund = self.init_invoice("out_refund", products=self.product_a)
        self.assertTrue(refund.with_user(billing_user).refund_reason_editable)
        refund.action_post()
        self.assertFalse(refund.with_user(billing_user).refund_reason_editable)
        self.assertTrue(refund.refund_reason_editable)

    def create_reversal(self, **values):
        return self.invoice_refund_obj.with_context(
            active_model="account.move",
            active_ids=self.account_invoice_customer0.ids,
        ).create(
            {
                "date": datetime.date.today(),
                "journal_id": self.account_invoice_customer0.journal_id.id,
                **values,
            }
        )

    def test_internal_reason_not_on_credit_note(self):
        self.reason_id.show_on_credit_note = False
        self.account_invoice_customer0.action_post()
        move_reversal = self.create_reversal(reason_id=self.reason_id.id)
        self.assertFalse(move_reversal.reason)
        move_reversal.refund_moves()
        refund = self.account_invoice_customer0.reversal_move_ids
        self.assertEqual(refund.reason_id, self.reason_id)
        self.assertEqual(
            refund.ref, f"Reversal of: {self.account_invoice_customer0.name}"
        )

    def test_custom_reason_text(self):
        self.account_invoice_customer0.action_post()
        move_reversal = self.create_reversal(
            reason_id=self.reason_id.id, reason="Discount on line 3 not applied"
        )
        move_reversal.refund_moves()
        refund = self.account_invoice_customer0.reversal_move_ids
        self.assertEqual(refund.reason_id, self.reason_id)
        self.assertEqual(
            refund.ref,
            f"Reversal of: {self.account_invoice_customer0.name}, "
            "Discount on line 3 not applied",
        )
