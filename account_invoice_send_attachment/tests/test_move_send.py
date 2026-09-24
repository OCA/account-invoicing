# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestMoveSend(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice("out_invoice", products=cls.product_a)
        cls.invoice.commercial_partner_id.email = "test@example.com"
        cls.invoice.commercial_partner_id.invoice_sending_method = "email"
        cls.attach1 = cls.env["ir.attachment"].create(
            {
                "name": "Attachment-1",
                "datas": "eW91IGN1cmlvdXM=",
                "res_model": "account.move",
                "res_id": cls.invoice.id,
            }
        )

    def test_01_move_send(self):
        """Test sending wizard"""
        vals = self.env["account.move.send"]._get_default_sending_settings(self.invoice)
        self.assertTrue(
            self.attach1.id in val.get("id") for val in vals["mail_attachments_widget"]
        )
