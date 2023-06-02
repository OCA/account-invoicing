# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountReceipt(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.in_receipt = cls.init_invoice(
            "in_receipt", products=cls.product_a + cls.product_b
        )
        cls.in_receipt._post()
        cls.out_receipt = cls.init_invoice(
            "out_receipt", products=cls.product_a + cls.product_b
        )
        cls.out_receipt._post()

    def test_receipt_mail_template(self):
        self.assertEqual(
            (self.in_receipt | self.out_receipt)._get_mail_template(),
            "account_receipt_send.email_template_edi_receipt",
            "Mail template chosen wrong",
        )
