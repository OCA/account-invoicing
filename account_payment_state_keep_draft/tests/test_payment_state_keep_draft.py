# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPaymentStateKeepDraft(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.bank_journal = cls.company_data["default_journal_bank"]

    def _make_invoice(self, move_type="out_invoice"):
        return self._create_invoice_one_line(
            move_type=move_type, price_unit=100.0, tax_ids=[], post=True
        )

    def _register_payment(self, invoice):
        """Register a payment for ``invoice`` through the standard wizard and
        return the created ``account.payment`` recordset."""
        wizard = (
            self.env["account.payment.register"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"journal_id": self.bank_journal.id})
        )
        return wizard._create_payments()

    def test_01_customer_payment_keep_draft(self):
        """Customer (inbound) payment configured to draft ends up in draft."""
        self.company.register_customer_payment_state = "draft"
        invoice = self._make_invoice("out_invoice")
        payment = self._register_payment(invoice)
        self.assertTrue(payment)
        self.assertEqual(payment.state, "draft")
        # The invoice is left open while the payment is kept on draft.
        self.assertEqual(invoice.payment_state, "not_paid")

    def test_02_vendor_payment_keep_draft(self):
        """Vendor (outbound) payment configured to draft ends up in draft."""
        self.company.register_vendor_payment_state = "draft"
        bill = self._make_invoice("in_invoice")
        payment = self._register_payment(bill)
        self.assertTrue(payment)
        self.assertEqual(payment.state, "draft")
        self.assertEqual(bill.payment_state, "not_paid")

    def test_03_default_posted_not_reset(self):
        """Default config (posted): ``_check_payment_draft`` is False, no reset."""
        self.assertEqual(self.company.register_customer_payment_state, "posted")
        invoice = self._make_invoice("out_invoice")
        payment = self._register_payment(invoice)
        self.assertTrue(payment)
        self.assertNotEqual(payment.state, "draft")

    def test_04_in_process_payment_keep_draft(self):
        """Regression: a payment landing on ``in_process`` must be reset too.

        In a community database the registered payment is promoted to ``paid``
        because ``account.move._get_invoice_in_payment_state`` returns ``paid``.
        We patch that hook to return ``in_payment`` (the behaviour once the
        Accounting app is installed) so the payment really stays ``in_process``,
        and we prove it is reset back to draft as well. This would fail with the
        previous ``state == "paid"`` only filter.
        """
        self.company.register_customer_payment_state = "draft"
        invoice = self._make_invoice("out_invoice")
        with patch.object(
            type(self.env["account.move"]),
            "_get_invoice_in_payment_state",
            lambda self: "in_payment",
        ):
            payment = self._register_payment(invoice)
            self.assertEqual(payment.state, "draft")

    def test_05_action_post_without_invoice(self):
        """``action_post`` override skips payments not linked to an invoice."""
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_a.id,
                "amount": 100.0,
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()
        self.assertFalse(payment.invoice_ids)
        self.assertNotEqual(payment.state, "draft")

    def test_06_draft_payment_reconciles_on_post(self):
        """A draft-kept payment reconciles its invoice once it is posted."""
        self.company.register_customer_payment_state = "draft"
        invoice = self._make_invoice("out_invoice")
        payment = self._register_payment(invoice)
        self.assertEqual(payment.state, "draft")
        self.assertEqual(invoice.payment_state, "not_paid")
        # Confirming the payment triggers the auto reconciliation handled by the
        # account.payment override of this module.
        payment.action_post()
        self.assertNotEqual(payment.state, "draft")
        self.assertEqual(invoice.payment_state, "paid")

    def test_07_draft_payment_keeps_invoice_links(self):
        """Resetting the payment to draft must keep its invoice links."""
        self.company.register_customer_payment_state = "draft"
        invoice = self._make_invoice("out_invoice")
        payment = self._register_payment(invoice)
        self.assertEqual(payment.state, "draft")
        self.assertEqual(payment.invoice_ids, invoice)
