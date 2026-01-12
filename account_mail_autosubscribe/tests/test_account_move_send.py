# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class AccountMoveSendWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Email Template
        mail_template_model = cls.env["mail.template"].with_context(
            test_mail_autosubscribe=True
        )
        cls.mail_template = mail_template_model.create(
            {
                "model_id": cls.env.ref("account.model_account_move").id,
                "name": "Invoice: Send by Mail",
                "subject": "Invoice: {{object.partner_id.name}}",
                "partner_to": "{{object.partner_id.id}}",
                "body_html": "Hello, this is an invoice",
            }
        )
        # Partners
        cls.commercial_partner = cls.env.ref("base.res_partner_4")
        cls.partner_1 = cls.env.ref("base.res_partner_address_13")
        cls.partner_2 = cls.env.ref("base.res_partner_address_14")
        cls.partner_3 = cls.env.ref("base.res_partner_address_24")
        # Autosubscribe rules
        cls.autosubscribe_move = cls.env.ref(
            "account_mail_autosubscribe.mail_autosubscribe_account_move"
        )
        cls.partner_3.mail_autosubscribe_ids = [(4, cls.autosubscribe_move.id)]
        # Invoice
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner_2.id,
                "invoice_date": fields.Date.today(),
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    fields.Command.create(
                        {
                            "product_id": cls.env.ref("product.product_product_7").id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.invoice.action_post()

    def _send_invoice(self):
        composer = (
            self.env["account.move.send.wizard"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create(
                {
                    "sending_methods": ["email"],
                    "mail_template_id": self.mail_template.id,
                }
            )
        )
        composer.action_send_and_print()
        return self.invoice.message_ids[0]

    def test_mail_message_composer(self):
        """Test invoice sending wizard with an autosubscribe follower."""
        message = self._send_invoice()
        self.assertEqual(message.partner_ids, self.partner_2 | self.partner_3)

    def test_mail_message_composer_disabled(self):
        """Test invoice sending wizard with no autosubscribe follower."""
        self.partner_3.mail_autosubscribe_ids = [(5, False)]
        message = self._send_invoice()
        self.assertEqual(message.partner_ids, self.partner_2)

    def test_mail_message_composer_no_autosubscribe_followers(self):
        """Test invoice sending wizard with autosubscribe disabled on the template."""
        self.mail_template.use_autosubscribe_followers = False
        message = self._send_invoice()
        self.assertEqual(message.partner_ids, self.partner_2)
