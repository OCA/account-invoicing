# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestWarnOptions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.partner_invoice_warn_warning = cls.env["warn.option"].create(
            {
                "name": "warning",
                "allowed_warning_usage": "partner_invoice_warn",
                "allowed_warning_type": "warning",
            }
        )
        cls.partner_invoice_warn_blocking = cls.env["warn.option"].create(
            {
                "name": "block",
                "allowed_warning_usage": "partner_invoice_warn",
                "allowed_warning_type": "block",
            }
        )

    def test_partner_warn_options(self):
        """Test Warn Options on Partner Form"""
        with Form(self.partner) as partner_f:
            partner_f.invoice_warn = "warning"
            partner_f.invoice_warn_option = self.partner_invoice_warn_warning
            self.assertEqual(partner_f.invoice_warn_msg, "warning")
            partner_f.invoice_warn = "block"
            partner_f.invoice_warn_option = self.partner_invoice_warn_blocking
            self.assertEqual(partner_f.invoice_warn_msg, "block")
