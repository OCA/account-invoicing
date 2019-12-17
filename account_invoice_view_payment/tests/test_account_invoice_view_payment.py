# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (https://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestAccountInvoiceViewPayment(TransactionCase):
    """
        Tests for Account Invoice View Payment.
    """

    def setUp(self):
        super(TestAccountInvoiceViewPayment, self).setUp()
        self.par_model = self.env["res.partner"]
        self.acc_model = self.env["account.account"]
        self.inv_model = self.env["account.move"]
        self.inv_line_model = self.env["account.move.line"]
        self.pay_model = self.env["account.payment"]
        self.reg_pay_model = self.env["account.payment.register"]

        self.cash = self.env["account.journal"].create(
            {"name": "Cash Test", "type": "cash", "code": "CT"}
        )
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )

        self.partner1 = self._create_partner()

        self.invoice_account = self.acc_model.search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )

        self.invoice1 = self._create_invoice(self.partner1, "out_invoice")
        self.invoice2 = self._create_invoice(self.partner1, "in_invoice")
        self.invoice3 = self._create_invoice(self.partner1, "in_invoice")

    def _create_partner(self):
        partner = self.par_model.create(
            {"name": "Test Partner", "company_type": "company"}
        )
        return partner

    def _create_invoice(self, partner, invoice_type):
        inv_line = [
            (
                0,
                0,
                {
                    "product_id": self.env.ref("product.product_product_8").id,
                    "name": "Test Invoice Line",
                    "account_id": self.invoice_account.id,
                    "quantity": 1.0,
                    "price_unit": 3.0,
                },
            )
        ]
        invoice = self.inv_model.create(
            {
                "partner_id": partner.id,
                "type": invoice_type,
                "invoice_line_ids": inv_line,
            }
        )
        return invoice

    def test_account_move_view_payment_out_invoice(self):
        self.invoice1.post()
        wiz = self.pay_model.with_context(
            active_id=[self.invoice1.id], active_model="account.move"
        ).create(
            {
                "journal_id": self.cash.id,
                "payment_method_id": self.payment_method_manual_in.id,
                "amount": self.invoice1.amount_residual,
                "payment_type": "inbound",
            }
        )

        res = wiz.post_and_open_payment()

        self.assertDictContainsSubset(
            {"type": "ir.actions.act_window", "res_model": "account.payment"},
            res,
            "There was an error and the view couldn't be opened.",
        )

        view_payment = self.invoice1.action_view_payments()

        self.assertDictContainsSubset(
            {"type": "ir.actions.act_window", "res_model": "account.payment"},
            view_payment,
            "There was an error and the invoice couldn't be paid.",
        )

    def test_account_move_view_payment_in_invoice(self):
        self.invoice2.post()
        wiz = self.pay_model.with_context(
            active_id=[self.invoice2.id], active_model="account.move"
        ).create(
            {
                "journal_id": self.cash.id,
                "payment_method_id": self.payment_method_manual_in.id,
                "amount": self.invoice2.amount_residual,
                "payment_type": "inbound",
            }
        )

        res = wiz.post_and_open_payment()

        self.assertDictContainsSubset(
            {"type": "ir.actions.act_window", "res_model": "account.payment"},
            res,
            "There was an error and the view couldn't be opened.",
        )

        view_payment = self.invoice2.action_view_payments()

        self.assertDictContainsSubset(
            {"type": "ir.actions.act_window", "res_model": "account.payment"},
            view_payment,
            "There was an error and the invoice couldn't be paid.",
        )

    def test_account_invoice_view_payment_multi(self):
        self.invoice2.post()
        self.invoice3.post()
        wiz = self.reg_pay_model.with_context(
            active_ids=[self.invoice2.id, self.invoice3.id], active_model="account.move"
        ).create(
            {
                "journal_id": self.cash.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )

        res = wiz.create_payment_and_open()

        self.assertDictContainsSubset(
            {"type": "ir.actions.act_window", "res_model": "account.payment"},
            res,
            "There was an error and the two invoices were not merged.",
        )
