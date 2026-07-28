# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountReceipt(AccountTestInvoicingCommon):
    def test_receipt_mail_template(self):
        receipt_mt = self.env.ref("account_receipt_send.email_template_edi_receipt")
        for move_type in {"out_receipt", "in_receipt"}:
            with self.subTest(move_type=move_type):
                receipt = self._create_invoice(move_type)
                self.assertEqual(
                    receipt._get_mail_template(),
                    receipt_mt,
                    "Mail template chosen wrong",
                )
