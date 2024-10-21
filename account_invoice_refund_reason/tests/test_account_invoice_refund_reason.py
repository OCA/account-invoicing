# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo.tests.common import TransactionCase


class TestAccountInvoiceRefundReason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.account_move_obj = cls.env["account.move"]
        cls.account_obj = cls.env["account.account"]
        cls.journal_obj = cls.env["account.journal"]
        cls.invoice_refund_obj = cls.env["account.move.reversal"]
        cls.reason_obj = cls.env["account.move.refund.reason"]

        cls.payment_term = cls.env.ref("account.account_payment_term_advance")
        cls.partner3 = cls.env.ref("base.res_partner_3")
        cls.product_id = cls.env.ref("product.product_product_5")

        cls.journal = cls.journal_obj.search([("type", "=", "sale")])
        if cls.journal:
            cls.journal = cls.journal[0]
        cls.account_id = cls.account_obj.search(
            [("account_type", "=", "income")], limit=1
        )
        cls.reason_id = cls.env["account.move.refund.reason"].create(
            {"name": "Cancellation"}
        )
        cls.other_reason_id = cls.env["account.move.refund.reason"].create(
            {"name": "Wrong Price"}
        )

        cls.account_rec1_id = cls.account_obj.create(
            dict(
                code="custacc",
                name="customer account",
                account_type="asset_receivable",
            )
        )
        cls.invoice_line_data = [
            (
                0,
                0,
                {
                    "product_id": cls.product_id.id,
                    "quantity": 10.0,
                    "account_id": cls.account_id.id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                },
            )
        ]

        cls.account_invoice_customer0 = cls.account_move_obj.create(
            dict(
                name="Test Customer Invoice",
                move_type="out_invoice",
                invoice_payment_term_id=cls.payment_term.id,
                journal_id=cls.journal.id,
                partner_id=cls.partner3.id,
                invoice_line_ids=cls.invoice_line_data,
            )
        )

    def create_refund_wizard(self, active_ids=None, **values):
        """Helper function to create a refund wizard"""
        if not active_ids:
            active_ids = self.account_invoice_customer0.ids

        create_values = dict(
            refund_method="refund",
            date=datetime.date.today(),
            reason_id=self.reason_id.id,
            journal_id=self.account_invoice_customer0.journal_id.id,
        )
        create_values.update(**values)
        account_invoice_refund = self.invoice_refund_obj.with_context(
            active_model="account.move", active_ids=active_ids
        ).create(create_values)
        self.assertEqual(
            account_invoice_refund.reason,
            account_invoice_refund.reason_id.name,
        )
        return account_invoice_refund

    def test_onchange_reason_id(self):
        self.account_invoice_customer0.action_post()
        self.account_invoice_refund_0 = self.create_refund_wizard()
        self.account_invoice_refund_0.reverse_moves()
        reversal_move = self.account_invoice_customer0.reversal_move_id
        self.assertEqual(reversal_move.reason_id.id, self.reason_id.id)

    def test_invoice_with_several_refunds(self):
        self.account_invoice_customer0.action_post()
        self.account_invoice_refund_0 = self.create_refund_wizard()
        self.account_invoice_refund_0.reverse_moves()
        reversal_move = self.account_invoice_customer0.reversal_move_id
        self.assertEqual(reversal_move.reason_id.id, self.reason_id.id)

        self.account_invoice_refund_1 = self.create_refund_wizard(
            reason_id=self.other_reason_id.id
        )
        self.account_invoice_refund_1.reverse_moves()
        reversal_move_2 = (
            self.account_invoice_customer0.reversal_move_id - reversal_move
        )
        self.assertEqual(reversal_move.reason_id.id, self.reason_id.id)
        self.assertEqual(reversal_move_2.reason_id.id, self.other_reason_id.id)

    def test_invoice_refund_modify(self):
        self.account_invoice_customer0.action_post()
        self.account_invoice_refund_0 = self.create_refund_wizard(
            refund_method="modify"
        )
        self.account_invoice_refund_0.reverse_moves()
        reversal_move = self.account_invoice_customer0.reversal_move_id
        self.assertEqual(reversal_move.reason_id.id, self.reason_id.id)

    def test_invoice_refund_several_invoices(self):
        self.account_invoice_customer1 = self.account_move_obj.create(
            dict(
                name="Test Customer Invoice 2",
                move_type="out_invoice",
                invoice_payment_term_id=self.payment_term.id,
                journal_id=self.journal.id,
                partner_id=self.partner3.id,
                invoice_line_ids=self.invoice_line_data,
            )
        )
        self.account_invoice_customer0.action_post()
        self.account_invoice_customer1.action_post()
        self.account_invoice_refund_0_1 = self.create_refund_wizard(
            active_ids=[
                self.account_invoice_customer0.id,
                self.account_invoice_customer1.id,
            ]
        )
        self.account_invoice_refund_0_1.reverse_moves()
        reversal_move0 = self.account_invoice_customer0.reversal_move_id
        self.assertEqual(reversal_move0.reason_id.id, self.reason_id.id)
        reversal_move1 = self.account_invoice_customer1.reversal_move_id
        self.assertEqual(reversal_move1.reason_id.id, self.reason_id.id)
