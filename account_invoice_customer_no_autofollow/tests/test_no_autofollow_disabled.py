# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from .common import NoAutofollowCommon


@tagged("post_install", "-at_install", "standart")
class TestNoAutofollow(NoAutofollowCommon):
    def setUp(self, *args, **kwargs):
        super(TestNoAutofollow, self).setUp(*args, **kwargs)

        self.env["ir.config_parameter"].sudo().set_param(
            "invoice_customer_no_autofollow.invoice_partner_no_autofollow", True,
        )
        self.invoice = (
            self.env["account.move"]
            .with_context(default_type="in_invoice")
            .create({"partner_id": self.partner1.id})
        )
        with Form(self.invoice) as form:
            with form.invoice_line_ids.new() as line_1:
                line_1.product_id = self.product1
            form.save()

    def test_message_subscribe_1(self):
        """'Customer no autofollow' mode is enabled in settings.
            Test whether the user will be added to the autofollow
        """
        self.invoice.with_context(
            invoice_no_auto_follow=self.invoice._partner_disable_autofollow()
        ).message_subscribe(partner_ids=[self.partner1.id])
        self.assertNotIn(
            self.invoice.partner_id.id,
            self.invoice.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_message_subscribe_2(self):
        """'Customer no autofollow' mode is enabled in settings.
            Test whether the user will be added to the autofollow
        """
        self.invoice.with_context(
            invoice_no_auto_follow=self.invoice._partner_disable_autofollow()
        ).message_subscribe([])
        self.assertNotIn(
            self.invoice.partner_id.id,
            self.invoice.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_message_subscribe_3(self):
        """'Customer no autofollow' mode is enabled in settings.
            Test whether the user will be added to the autofollow
        """
        self.invoice.with_context(
            invoice_no_auto_follow=self.invoice._partner_disable_autofollow()
        ).message_subscribe()
        self.assertNotIn(
            self.invoice.partner_id.id,
            self.invoice.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_partner_disable_autofollow(self):
        """
        'Customer no autofollow' disabled is enabled in settings.
        Test whether the option to disable autofollow is enabled
        or disabled
        """
        self.assertEqual(
            self.invoice._partner_disable_autofollow(), "True", "Must be equal to True",
        )

    def test_in_invoice_create(self):
        """
        'Customer no autofollow' mode is enabled in settings.
        Test if there is a client among subscribers when creating a invoice.
        """
        self.assertNotIn(
            self.invoice.partner_id.id,
            self.invoice.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_in_invoice_action_post(self):
        """
        'Customer no autofollow' mode is enabled in settings.
        Test if there is a customer among the subscribers
        after confirming the invoice.
        """
        self.invoice.action_post()
        self.assertNotIn(
            self.invoice.partner_id.id,
            self.invoice.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )
