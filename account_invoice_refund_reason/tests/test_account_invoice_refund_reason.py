# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

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

        if refund_method == "refund":
            move_reversal.refund_moves()
        else:
            move_reversal.modify_moves()
        account_invoice_refund = move_reversal.new_move_ids

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
