# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from odoo.addons.account.tests.test_account_move_send import TestAccountMoveSendCommon


@tagged("post_install_l10n", "post_install", "-at_install", "mail_template")
class TestAccountMoveSend(TestAccountMoveSendCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_data_2 = cls.setup_other_company()
        (
            cls.partner_a.with_company(cls.company_data["company"].id)
            + cls.partner_b.with_company(cls.company_data["company"].id)
        ).write(
            {
                "invoice_sending_method": "email",
                "email": "turlututu@tsointsoin",
            }
        )
        (
            cls.partner_a.with_company(cls.company_data_2["company"].id)
            + cls.partner_b.with_company(cls.company_data_2["company"].id)
        ).write(
            {
                "invoice_sending_method": "email",
                "email": "turlututu@tsointsoin",
            }
        )

    def test_invoice_mail_attachments_widget(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True)

        extra_attachment = self.env["ir.attachment"].create(
            {"name": "extra_attachment", "raw": b"bar"}
        )

        # Attach a new ... attachment
        invoice.attachment_ids |= extra_attachment
        invoice.to_be_sent_attachment_ids |= extra_attachment

        wizard = self.create_send_and_print(
            invoice,
            sending_methods=["email"],
        )
        pdf_report_values = {
            "mimetype": "application/pdf",
            "name": "INV_2019_00001.pdf",
            "placeholder": True,
        }
        extra_attachment_values = {
            "mimetype": "application/octet-stream",
            "name": extra_attachment.name,
            "placeholder": False,
        }

        self._assert_mail_attachments_widget(
            wizard, [pdf_report_values, extra_attachment_values]
        )
