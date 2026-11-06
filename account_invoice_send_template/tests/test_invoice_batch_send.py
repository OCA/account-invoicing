# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import tagged

from odoo.addons.account.tests.test_account_move_send import (
    TestAccountComposerPerformance,
    TestAccountMoveSendCommon,
)


@tagged("post_install", "-at_install")
class InvoiceBatchSend(TestAccountComposerPerformance, TestAccountMoveSendCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_invoice_send_with_mail_template_from_wizard(self):
        invoice1 = self.init_invoice(
            "out_invoice", partner=self.partner_a, amounts=[1000], post=True
        )
        invoice2 = self.init_invoice(
            "out_invoice", partner=self.partner_b, amounts=[1000], post=True
        )
        self.partner_a.invoice_sending_method = "email"
        self.partner_b.invoice_sending_method = "email"
        wizard = self.create_send_and_print(invoice1 + invoice2)
        mail_template = self.move_template.copy()
        mail_template.name = "Test account send email"
        self.assertNotEqual(mail_template, invoice1._get_mail_template())
        wizard.mail_template_id = mail_template
        wizard.action_send_and_print()
        self.assertEqual(mail_template, invoice1._get_mail_template())
        self.assertEqual(mail_template, wizard._get_default_mail_template_id(invoice1))
        self.assertEqual(mail_template, wizard._get_default_mail_template_id(invoice2))

    def test_invoice_send_with_default_mail_template(self):
        invoice1 = self.init_invoice(
            "out_invoice", partner=self.partner_a, amounts=[1000], post=True
        )
        invoice2 = self.init_invoice(
            "out_invoice", partner=self.partner_b, amounts=[1000], post=True
        )
        self.partner_a.invoice_sending_method = "email"
        self.partner_b.invoice_sending_method = "email"
        wizard = self.create_send_and_print(invoice1 + invoice2)
        # Default mail template
        self.assertEqual(
            wizard._get_default_mail_template_id(invoice1),
            self.env.ref("account.email_template_edi_invoice"),
        )
        wizard.action_send_and_print()
        self.assertEqual(
            wizard._get_default_mail_template_id(invoice1),
            self.env.ref("account.email_template_edi_invoice"),
        )
