# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestAccountInvoiceMergePayment(TransactionCase):
    """
    Tests for Account Invoice Merge Payment.
    """

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceMergePayment, cls).setUpClass()
        cls.par_model = cls.env["res.partner"]
        cls.context = cls.env["res.users"].context_get()
        cls.acc_model = cls.env["account.account"]
        cls.inv_model = cls.env["account.move"]
        cls.inv_line_model = cls.env["account.move.line"]
        cls.wiz = cls.env["invoice.merge"]
        cls.payment_mode_model = cls.env["account.payment.mode"]
        cls.journal_model = cls.env["account.journal"]

        cls.journal_c1 = cls.journal_model.create(
            {
                "name": "J1",
                "code": "J1",
                "type": "bank",
                "bank_acc_number": "123456",
            }
        )
        cls.partner1 = cls.par_model.create({"name": "Test Partner"})
        cls.payment_mode_1 = cls._payment_mode("Pay mode 1")
        cls.payment_mode_2 = cls._payment_mode("Pay mode 2")
        cls.invoice_account = cls.acc_model.search(
            [("account_type", "=", "asset_receivable")],
            limit=1,
        )
        cls.invoice1 = cls._create_invoice(
            cls.partner1, cls.payment_mode_1.id, cls.invoice_account.id
        )
        cls.invoice2 = cls._create_invoice(
            cls.partner1, cls.payment_mode_1.id, cls.invoice_account.id
        )

    @classmethod
    def _create_invoice(cls, partner, payment_mode_id, account_id):
        invoice = cls.inv_model.create(
            {
                "partner_id": partner.id,
                "payment_mode_id": payment_mode_id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test invoice line",
                            "account_id": account_id,
                            "quantity": 1.0,
                            "price_unit": 1.0,
                            "product_id": cls.env.ref("product.product_product_2").id,
                        },
                    )
                ],
            }
        )
        return invoice

    @classmethod
    def _payment_mode(cls, name):
        payment_mode = cls.payment_mode_model.create(
            {
                "name": name,
                "bank_account_link": "fixed",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "fixed_journal_id": cls.journal_c1.id,
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
            active_model="account.move",
        ).create({})
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
            active_model="account.move",
        ).create({})
        self.assertEqual(
            wiz_id.error_message,
            "All invoices must have the same: \n- Payment Mode",
        )
