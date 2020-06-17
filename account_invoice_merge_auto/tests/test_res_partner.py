from odoo.tests.common import at_install, post_install

from .common import AutoMergeInvoiceTC


@at_install(False)
@post_install(True)
class PartnerTC(AutoMergeInvoiceTC):

    def _partner_invoices(self, partner):
        return self.env['account.invoice'].search([
            ('partner_id', '=', partner.id),
        ])

    def test_cron(self):
        inv_1 = self.create_invoice(self.partner_1, '2019-05-01', 5)
        inv_2 = self.create_invoice(self.partner_1, '2019-05-04', 10)
        inv_3 = self.create_invoice(self.partner_1, '2019-05-16', 20)
        old_invoices = self._partner_invoices(self.partner_1)

        self.env['res.partner']._cron_invoice_merge('2019-05-17')

        self.assertEqual(inv_1.state, 'cancel')
        self.assertEqual(inv_2.state, 'cancel')
        self.assertEqual(inv_3.state, 'draft')

        other_inv = self._partner_invoices(self.partner_1) - old_invoices
        self.assertEqual(len(other_inv), 1)
        self.assertEqual(other_inv.amount_total, 15)
        self.assertEqual(other_inv.state, 'draft')
        self.assertEqual(other_inv.date_invoice, '2019-05-17')
        self.assertEqual(self.partner_1.invoice_merge_next_date, '2019-06-15')
