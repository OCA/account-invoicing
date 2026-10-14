# Copyright 2023 bosd (<bosd>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSubstate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.substate_test_account_move = self.env["account.move"]

        self.substate_to_verify = self.env.ref(
            "account_move_substate.base_substate_to_verify_account_move"
        )
        self.substate_checked = self.env.ref(
            "account_move_substate.base_substate_checked_account_move"
        )
        self.substate_verified = self.env.ref(
            "account_move_substate.base_substate_verified_account_move"
        )
        self.mail_template_verified = self.env.ref(
            "account_move_substate.mail_template_data_account_move_substate_verified"
        )

        self.product = self.env["product.product"].create({"name": "Test"})

    def _create_customer_invoice(self):
        partner = self.env.ref("base.res_partner_12")
        return self.substate_test_account_move.create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "quantity": 1,
                            "price_unit": 450,
                            "tax_ids": [(6, 0, [])],
                        },
                    )
                ],
            }
        )

    def test_account_move_substate(self):
        invoice_test1 = self._create_customer_invoice()

        self.assertTrue(invoice_test1.state == "draft")

        with self.assertRaises(ValidationError):
            invoice_test1.substate_id = self.substate_verified
        # post the invoice
        invoice_test1.action_post()
        self.assertTrue(invoice_test1.substate_id == self.substate_verified)

        # test that there is no substate id
        invoice_test1.button_cancel()
        self.assertTrue(invoice_test1.state == "cancel")
        self.assertTrue(not invoice_test1.substate_id)

    def test_track_template_without_mail_template(self):
        invoice = self._create_customer_invoice()

        tracked_templates = invoice._track_template({"substate_id": True})

        self.assertNotIn("substate_id", tracked_templates)

    def test_track_template_with_mail_template(self):
        invoice = self._create_customer_invoice()
        invoice.action_post()

        tracked_templates = invoice._track_template({"substate_id": True})

        self.assertEqual(
            tracked_templates["substate_id"][0], self.mail_template_verified
        )
        self.assertEqual(
            tracked_templates["substate_id"][1]["composition_mode"], "comment"
        )
        self.assertEqual(
            tracked_templates["substate_id"][1]["subtype_id"],
            self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_note"),
        )
        self.assertEqual(
            tracked_templates["substate_id"][1]["email_layout_xmlid"],
            "mail.mail_notification_light",
        )
