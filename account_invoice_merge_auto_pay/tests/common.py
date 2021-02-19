from odoo import fields
from odoo.tests.common import at_install, post_install

from odoo.addons.account_invoice_merge_auto.tests.common import \
    AutoMergeInvoiceTC


def fake_do_tx_ok(self, *args, **kwargs):
    return True


@at_install(False)
@post_install(True)
class AutoPayInvoiceTC(AutoMergeInvoiceTC):

    def setUp(self):
        super(AutoPayInvoiceTC, self).setUp()
        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))
        # Maybe the acquirer should be chosen more carefully
        acquirer = self.env["payment.acquirer"].search([
            ("name", "=", "Ingenico")]).ensure_one()
        self.partner_1.payment_token_id = self.env["payment.token"].create({
            "name": "test payment token",
            "partner_id": self.partner_1.id,
            "acquirer_id": acquirer.id,
            "acquirer_ref": "test ref",
        })
        self.partner_1.customer_payment_mode_id = False
        sale_journal = self.env["account.journal"].search([
            ("type", "=", "bank")], limit=1)
        pmethod = self.env.ref("payment.account_payment_method_electronic_in")
        self.payment_mode = self.env["account.payment.mode"].create({
            "name": "customer automatic payment",
            "payment_method_id": pmethod.id,
            "payment_type": "inbound",
            "bank_account_link": "fixed",
            "fixed_journal_id": sale_journal.id,
        })

    def _multiple_invoice_merge_test(self, invoices=None, **params):
        params.setdefault("payment_mode_id", self.payment_mode.id)
        if not invoices:
            invoices = [self.create_invoice(self.partner_1, date, **params)
                        for date in ("2019-05-09", "2019-05-10")]

        Invoice = self.env["account.invoice"]
        _invs, merge_infos = Invoice._cron_invoice_merge("2019-05-16")

        self.assertEqual(len(merge_infos), 1)
        new_inv = Invoice.browse(
            list(merge_infos.keys())[0])
        self.assertEqual(
            new_inv.date_invoice,
            fields.Date.from_string("2019-05-16"))
        self.assertEqual(
            {inv.id for inv in invoices},
            set(merge_infos[new_inv.id]))
        self.assertTrue(all(inv.state == "cancel" for inv in invoices))
        self.assertEqual(
            self.partner_1.invoice_merge_next_date,
            fields.Date.from_string("2019-06-15"))
        return new_inv
