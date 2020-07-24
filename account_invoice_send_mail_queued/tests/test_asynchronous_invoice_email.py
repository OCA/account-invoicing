# Copyright 2020 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestAsynchronousInvoiceEmail(common.TransactionCase):
    def setUp(self):
        super(TestAsynchronousInvoiceEmail, self).setUp()
        self.account_invoice_send_obj = self.env["account.invoice.send"]
        self.job_obj = self.env["queue.job"]
        self.invoice_obj = self.env["account.move"]

    def test_delay_send_invoices(self):
        invoices = self.env["account.move"].search([("type", "=", "out_invoice")]).ids
        template_id = self.env.ref("account.email_template_edi_invoice").id
        context = {
            "active_ids": invoices,
            "lang": "en_US",
        }
        wizard_email = self.account_invoice_send_obj.with_context(context).create(
            {"composition_mode": "mass_mail", "template_id": template_id}
        )
        nbr_job = len(self.job_obj.search([]))
        wizard_email.with_context(context)._send_email()
        new_nbr_job = len(self.job_obj.search([]))
        self.assertEqual(new_nbr_job, nbr_job + 1)
