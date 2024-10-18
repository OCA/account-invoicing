# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountInvoiceMergePayment(TransactionCase):
    """
    Tests for Account Invoice Merge Payment.
    """

    def setUp(self):
        super(TestAccountInvoiceMergePayment, self).setUp()
        self.par_model = self.env["res.partner"]
        self.context = self.env["res.users"].context_get()
        self.acc_model = self.env["account.account"]
        self.inv_model = self.env["account.invoice"]
        self.inv_line_model = self.env["account.invoice.line"]
        self.wiz = self.env["invoice.merge"]
        self.payment_mode_model = self.env["account.payment.mode"]
        self.journal_model = self.env["account.journal"]

        self.journal_c1 = self.journal_model.create(
            {
                "name": "J1",
                "code": "J1",
                "type": "bank",
                "bank_acc_number": "123456",
            }
        )
        self.partner1 = self.par_model.create({"name": "Test Partner"})
        self.payment_mode_1 = self._payment_mode("Pay mode 1")
        self.payment_mode_2 = self._payment_mode("Pay mode 2")
        self.invoice_account = self.acc_model.search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        self.invoice1 = self._create_invoice(
            self.partner1, self.payment_mode_1.id, self.invoice_account.id
        )
        self.invoice2 = self._create_invoice(
            self.partner1, self.payment_mode_1.id, self.invoice_account.id
        )

    def _create_invoice(self, partner, payment_mode_id, account_id):
        invoice = self.inv_model.create(
            {
                "partner_id": partner.id,
                "payment_mode_id": payment_mode_id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test invoice line",
                            "account_id": account_id,
                            "quantity": 1.0,
                            "price_unit": 1.0,
                            "product_id": self.env.ref("product.product_product_2").id,
                        },
                    )
                ],
            }
        )
        return invoice

    def _payment_mode(self, name):
        payment_mode = self.payment_mode_model.create(
            {
                "name": name,
                "bank_account_link": "fixed",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "fixed_journal_id": self.journal_c1.id,
            }
        )
        return payment_mode

    def test_account_invoice_merge_same_payment_mode(self):
        start_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(start_inv), 2)

        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice2.id],
            active_model="account.invoice",
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(end_inv), 1)

    def test_account_invoice_merge_diff_payment_mode(self):
        self.invoice3 = self._create_invoice(
            self.partner1, self.payment_mode_2.id, self.invoice_account.id
        )
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice3.id],
            active_model="account.invoice",
        ).create({})
        with self.assertRaises(UserError):
            wiz_id.fields_view_get()
