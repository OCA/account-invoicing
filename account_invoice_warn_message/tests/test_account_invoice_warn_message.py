# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestAccountInvoiceWarnMessage(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
            }
        )
        cls.warn_msg_parent = "This company has payment issues"
        cls.parent = cls.env["res.partner"].create(
            {
                "name": "ACME Corp",
                "email": "acme@example.com",
                "invoice_warn_msg": cls.warn_msg_parent,
            }
        )
        cls.warn_msg = "Contact-specific invoice warning"
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "ACME Contact",
                "email": "contact@acme.com",
                "invoice_warn_msg": cls.warn_msg,
            }
        )

    def _make_invoice(self, move_type="out_invoice", partner=None):
        vals = {
            "move_type": move_type,
            "invoice_line_ids": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "quantity": 1,
                        "price_unit": 42,
                    }
                ),
            ],
        }
        if partner is not None:
            vals["partner_id"] = partner.id
        return self.env["account.move"].create(vals)

    def test_compute_invoice_warn_msg(self):
        invoice = self._make_invoice(partner=self.partner)
        self.assertEqual(
            invoice.invoice_warn_msg,
            f"{self.partner.name} - {self.warn_msg}",
        )

    def test_compute_invoice_warn_msg_parent(self):
        self.partner.parent_id = self.parent
        invoice = self._make_invoice(partner=self.partner)
        self.assertEqual(
            invoice.invoice_warn_msg,
            f"{self.parent.name} - {self.warn_msg_parent}"
            f"\n{self.partner.name} - {self.warn_msg}",
        )

    def test_compute_invoice_warn_msg_parent_but_not_partner(self):
        self.partner.write({"invoice_warn_msg": False, "parent_id": self.parent.id})
        invoice = self._make_invoice(partner=self.partner)
        self.assertEqual(
            invoice.invoice_warn_msg,
            f"{self.parent.name} - {self.warn_msg_parent}",
        )

    def test_compute_invoice_warn_msg_in_invoice(self):
        invoice = self._make_invoice(move_type="in_invoice", partner=self.partner)
        self.assertFalse(invoice.invoice_warn_msg)

    def test_compute_invoice_warn_msg_posted_state(self):
        invoice = self._make_invoice(partner=self.partner)
        invoice.action_post()
        self.assertFalse(invoice.invoice_warn_msg)

    def test_compute_invoice_warn_msg_no_partner(self):
        invoice = self._make_invoice()
        self.assertFalse(invoice.invoice_warn_msg)

    def test_compute_invoice_warn_msg_no_warnings(self):
        partner_no_warn = self.env["res.partner"].create(
            {
                "name": "Customer without warning",
                "email": "customer@nowarn.com",
            }
        )
        parent_no_warn = self.env["res.partner"].create(
            {
                "name": "Parent without warning",
                "email": "parent@nowarn.com",
            }
        )
        partner_no_warn.parent_id = parent_no_warn.id
        invoice = self._make_invoice(partner=partner_no_warn)
        self.assertFalse(invoice.invoice_warn_msg)
