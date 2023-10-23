# Copyright 2023 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInvoiceRefundCode(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )

        cls.out_invoice = cls.init_invoice(
            "out_invoice", products=cls.product_a + cls.product_b
        )
        cls.out_invoice._post()
        cls.journal = cls.out_invoice.journal_id

    def test_invoice_refund_code_01(self):

        refund_code = "TEST"

        self.journal.write(
            {
                "refund_code": refund_code,
            }
        )
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_id=self.out_invoice.id,
                active_model=self.out_invoice._name,
                active_ids=self.out_invoice.ids,
            )
            .create(
                {
                    "journal_id": self.journal.id,
                }
            )
        )

        action = reversal.reverse_moves()
        refund = self.env[action["res_model"]].browse(action["res_id"])

        name = refund.name.split("/")
        self.assertEqual(name[0], refund_code)
