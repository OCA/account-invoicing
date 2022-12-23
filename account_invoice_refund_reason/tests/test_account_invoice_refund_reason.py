# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo.tests.common import SavepointCase


class TestAccountInvoiceRefundReason(SavepointCase):
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
        cls.account_user_type = cls.env.ref("account.data_account_type_receivable")
        cls.product_id = cls.env.ref("product.product_product_5")
        cls.account_revenue = cls.env.ref("account.data_account_type_revenue")

        cls.journal = cls.journal_obj.search([("type", "=", "sale")])
        if cls.journal:
            cls.journal = cls.journal[0]
        cls.account_id = cls.account_obj.search(
            [("user_type_id", "=", cls.account_revenue.id)], limit=1
        )
        cls.reason_id = cls.env["account.move.refund.reason"].create(
            {"name": "Cancellation"}
        )

        cls.account_rec1_id = cls.account_obj.create(
            dict(
                code="cust_acc",
                name="customer account",
                user_type_id=cls.account_user_type.id,
                reconcile=True,
            )
        )
        invoice_line_data = [
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
                invoice_line_ids=invoice_line_data,
            )
        )

    def test_onchange_reason_id(self):
        self.account_invoice_customer0.action_post()
        self.account_invoice_refund_0 = self.invoice_refund_obj.with_context(
            active_model="account.move", active_ids=self.account_invoice_customer0.ids
        ).create(
            dict(
                refund_method="refund",
                date=datetime.date.today(),
                reason_id=self.reason_id.id,
                journal_id=self.account_invoice_customer0.journal_id.id,
            )
        )
        self.account_invoice_refund_0._onchange_reason_id()
        self.assertEqual(
            self.account_invoice_refund_0.reason,
            self.account_invoice_refund_0.reason_id.name,
        )
        self.account_invoice_refund_0.reverse_moves()
        reversal_move = self.account_invoice_customer0.reversal_move_id
        self.assertEqual(reversal_move.reason_id.id, self.reason_id.id)
