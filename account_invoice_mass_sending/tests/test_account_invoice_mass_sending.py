# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import TransactionCase

from odoo.addons.queue_job.tests.common import trap_jobs


class TestAccountInvoiceMassSending(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.wizard_obj = cls.env["account.invoice.send"]
        cls.invoice_obj = cls.env["account.move"]
        cls.mail_template_obj = cls.env["mail.template"]

        cls.partner_with_email = cls.env["res.partner"].create(
            {"name": "Test partner 1", "email": "test@mail.com"}
        )
        cls.partner_without_mail = cls.env["res.partner"].create(
            {
                "name": "Test partner 2",
            }
        )

        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TESTAIMS",
                "account_type": "equity",
            }
        )
        cls.first_eligible_invoice = cls.invoice_obj.create(
            {
                "partner_id": cls.partner_with_email.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "account_id": cls.account.id,
                            "price_unit": 20.0,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )
        cls.second_eligible_invoice = cls.invoice_obj.create(
            {
                "partner_id": cls.partner_with_email.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "account_id": cls.account.id,
                            "price_unit": 20.0,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )
        cls.invoice_without_mail = cls.invoice_obj.create(
            {
                "partner_id": cls.partner_without_mail.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "account_id": cls.account.id,
                            "price_unit": 20.0,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )
        cls.invoice_in_progress = cls.invoice_obj.create(
            {
                "partner_id": cls.partner_with_email.id,
                "move_type": "out_invoice",
                "sending_in_progress": True,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "account_id": cls.account.id,
                            "price_unit": 20.0,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )

    def test_invoice_mass_sending_1(self):
        # test two eligible invoice to send
        self.invoices = self.first_eligible_invoice + self.second_eligible_invoice
        with trap_jobs() as trap:
            wizard = self.wizard_obj.with_context(
                active_ids=self.invoices.ids,
                active_model=self.first_eligible_invoice._name,
                discard_logo_check=True,
            ).create({})
            wizard.enqueue_invoices()
            trap.assert_jobs_count(2)

    def test_invoice_mass_sending_2(self):
        # test no invoice to send (one in progress)
        with trap_jobs() as trap:
            wizard = self.wizard_obj.with_context(
                active_ids=self.invoice_in_progress.ids,
                active_model=self.invoice_in_progress._name,
                discard_logo_check=True,
            ).create({})
            wizard.enqueue_invoices()
            trap.assert_jobs_count(0)

    def test_invoice_mass_sending_3(self):
        # test one invoice to send, one with no mail and one already in progress
        self.invoices = (
            self.first_eligible_invoice
            + self.invoice_without_mail
            + self.invoice_in_progress
        )
        with trap_jobs() as trap:
            wizard = self.wizard_obj.with_context(
                active_ids=self.invoices.ids,
                active_model=self.first_eligible_invoice._name,
                discard_logo_check=True,
            ).create({})
            wizard.enqueue_invoices()
            self.assertTrue(self.first_eligible_invoice.sending_in_progress)
            self.assertFalse(self.invoice_without_mail.sending_in_progress)
            self.assertTrue(self.invoice_in_progress.sending_in_progress)
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                self.first_eligible_invoice._send_invoice_individually,
                kwargs={"template": self.mail_template_obj},
            )
            trap.perform_enqueued_jobs()
            self.assertFalse(self.first_eligible_invoice.sending_in_progress)

    def _create_attachment(self, invoice):
        document = self.env["ir.attachment"].create(
            {
                "name": "EDI Document",
                "res_model": "account.move",
                "res_id": invoice.id,
                "mimetype": "application/xml",
            }
        )
        return document

    def create_edi_document(self, state, move=None, move_type=None):
        edi_format = (
            self.env["account.edi.format"]
            .sudo()
            .create(
                {
                    "name": "test_edi_format",
                    "code": "test_edi_format",
                }
            )
        )
        return self.env["account.edi.document"].create(
            {"edi_format_id": edi_format.id, "move_id": move.id, "state": state}
        )

    def test_invoice_mass_sending_4(self):
        # test one invoice to send with edi document attached
        invoice = self.first_eligible_invoice
        attachment = self._create_attachment(invoice)
        edi_document = self.create_edi_document("sent", invoice, invoice.move_type)
        edi_document.attachment_id = attachment.id
        self.assertEqual(len(invoice.edi_document_ids), 1)
        self.assertEqual(len(invoice.attachment_ids), 1)
        with trap_jobs() as trap:
            wizard = self.wizard_obj.with_context(
                active_ids=invoice.ids,
                active_model=self.first_eligible_invoice._name,
                discard_logo_check=True,
            ).create({})
            wizard.enqueue_invoices()
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                invoice._send_invoice_individually,
                kwargs={"template": self.mail_template_obj},
            )
            trap.perform_enqueued_jobs()
            mail = self.env["mail.mail"].search(
                [("model", "=", "account.move"), ("res_id", "=", invoice.id)]
            )
            self.assertTrue(mail)
            attachment_ids = mail.attachment_ids.ids
            self.assertIn(attachment_ids[0], invoice.attachment_ids.ids)
