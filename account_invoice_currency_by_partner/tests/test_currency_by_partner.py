# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveCurrency(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Journal = cls.env["account.journal"]
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.vendor_currency = cls.env.ref("base.GBP")
        cls.customer_currency = cls.env.ref("base.EUR")
        cls.partner.vendor_currency_id = cls.vendor_currency
        cls.partner.customer_currency_id = cls.customer_currency
        cls.journal_in = cls.Journal.create(
            {
                "name": "Purchase Journal",
                "code": "PUR",
                "type": "purchase",
            }
        )
        cls.journal_out = cls.Journal.create(
            {
                "name": "Sales Journal",
                "code": "SAL",
                "type": "sale",
            }
        )

    def _create_move(self, move_type, journal):
        """Helper to create minimal account.move with optional pricelist."""
        vals = {
            "move_type": move_type,
            "partner_id": self.partner.id,
            "journal_id": journal.id,
        }
        move = self.env["account.move"].create(vals)
        return move

    def test_vendor_invoice_uses_vendor_currency(self):
        move = self._create_move("in_invoice", self.journal_in)
        self.assertEqual(
            move.currency_id,
            self.vendor_currency,
            "Vendor invoices must use vendor_currency_id",
        )

    def test_vendor_refund_uses_vendor_currency(self):
        move = self._create_move("in_refund", self.journal_in)
        self.assertEqual(
            move.currency_id,
            self.vendor_currency,
            "Vendor refunds must use vendor_currency_id",
        )

    def test_customer_invoice_uses_customer_currency(self):
        move = self._create_move("out_invoice", self.journal_out)
        self.assertEqual(
            move.currency_id,
            self.customer_currency,
            "Customer invoices must use customer_currency_id",
        )

    def test_customer_refund_uses_customer_currency(self):
        move = self._create_move("out_refund", self.journal_out)
        self.assertEqual(
            move.currency_id,
            self.customer_currency,
            "Customer refunds must use customer_currency_id",
        )
