# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.base.tests.common import BaseCommon


class TestAccountMoveSend(BaseCommon):
    """
    Tests invoice email subject rendering (Odoo 19 safe version)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("account.email_template_edi_invoice")
        cls.partner_custom = cls.env["res.partner"].create(
            {
                "name": "Partner Custom",
                "email": "custom@example.com",
                "invoice_email_subject": "Test invoice {{ object.name }}",
            }
        )
        cls.partner_default = cls.env["res.partner"].create(
            {
                "name": "Partner Default",
                "email": "default@example.com",
                "invoice_email_subject": "",
            }
        )
        cls.invoice_custom = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_custom.id,
                "invoice_date": "2026-01-23",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        cls.invoice_custom.action_post()
        cls.invoice_default = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_default.id,
                "invoice_date": "2026-01-23",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product 2",
                            "quantity": 2,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        cls.invoice_default.action_post()

    def _get_subject(self, move):
        return self.env["account.move.send"]._get_default_mail_subject(
            move,
            self.template,
            move.partner_id.lang,
        )

    def test_custom_subject_rendering(self):
        subject = self._get_subject(self.invoice_custom)
        self.assertTrue(subject)
        self.assertIn("Test invoice", subject)
        self.assertIn(self.invoice_custom.name, subject)

    def test_default_subject_fallback(self):
        subject = self._get_subject(self.invoice_default)
        self.assertTrue(subject)
        self.assertIn(self.invoice_default.name, subject)

    def test_child_partner_inherits_commercial(self):
        child = self.env["res.partner"].create(
            {
                "name": "Child Partner",
                "parent_id": self.partner_custom.id,
            }
        )
        invoice = self.invoice_custom.copy(
            {
                "partner_id": child.id,
            }
        )
        invoice.action_post()
        subject = self._get_subject(invoice)
        self.assertTrue(subject)
        self.assertIn(invoice.name, subject)

    def test_batch_behavior(self):
        """Ensure subject logic is deterministic per invoice"""
        moves = [self.invoice_custom, self.invoice_default]
        subjects = {move.id: self._get_subject(move) for move in moves}
        self.assertTrue(subjects[self.invoice_custom.id])
        self.assertIn("Test invoice", subjects[self.invoice_custom.id])
        self.assertTrue(subjects[self.invoice_default.id])
        self.assertIn(self.invoice_default.name, subjects[self.invoice_default.id])
