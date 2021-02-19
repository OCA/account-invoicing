from mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import at_install, post_install

from odoo.addons.payment.models.payment_acquirer import PaymentTransaction

from .common import AutoPayInvoiceTC, fake_do_tx_ok


@at_install(False)
@post_install(True)
class ResPartnerTC(AutoPayInvoiceTC):

    def test_no_payment_mode(self):
        with self.assertRaises(ValidationError) as err:
            self.create_invoice(self.partner_1, "2019-05-09",
                                # Useless but explicit is better than implicit:
                                payment_mode_id=False)
        self.assertEqual("Payment mode is needed to auto pay an invoice",
                         err.exception.name)

    def test_no_more_payment_mode(self):
        inv = self.create_invoice(self.partner_1, "2019-05-10",
                                  payment_mode_id=self.payment_mode.id)
        with self.assertRaises(ValidationError) as err:
            inv.update({"payment_mode_id": False})
        self.assertEqual("Payment mode is needed to auto pay an invoice",
                         err.exception.name)

    def test_do_not_pay_refund(self):
        "Do not pay refunds, but do not prevent their merge"
        with patch.object(PaymentTransaction, "s2s_do_transaction") as autopay:
            new_inv = self._multiple_invoice_merge_test(type="out_refund")
        autopay.assert_not_called()
        self.assertEqual(new_inv.state, "draft")

    def test_auto_pay_merged_invoices(self):
        with patch.object(PaymentTransaction, "s2s_do_transaction",
                          fake_do_tx_ok):
            new_inv = self._multiple_invoice_merge_test()
        self.assertEqual(new_inv.state, "paid")

    def test_auto_pay_single_invoices(self):
        inv = self.create_invoice(self.partner_1, "2019-05-10",
                                  payment_mode_id=self.payment_mode.id)
        with patch.object(PaymentTransaction, "s2s_do_transaction",
                          fake_do_tx_ok):
            _invs, merge_infos = inv._cron_invoice_merge("2019-05-16")
        self.assertFalse(merge_infos)
        self.assertEqual(inv.state, "paid")
        self.assertEqual(inv.date_invoice, fields.Date.from_string("2019-05-10"))
        self.assertEqual(self.partner_1.invoice_merge_next_date,
                         fields.Date.from_string("2019-06-15"))

    def test_auto_pay_no_token_error(self):
        self.partner_1.payment_token_id = False
        with self.assertRaises(ValidationError) as err:
            with patch.object(PaymentTransaction, "s2s_do_transaction",
                              fake_do_tx_ok):
                self._multiple_invoice_merge_test()
        self.assertIn("No payment token", err.exception.name)
