# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.account.tests.test_account_move_send import TestAccountMoveSendCommon
from odoo.addons.queue_job.tests.common import trap_jobs


class TestAccountMoveMassSending(TestAccountMoveSendCommon):
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
        cls.wizard_obj = cls.env["account.move.send"]
        cls.mail_template_obj = cls.env["mail.template"]

        cls.partner_with_email = cls.env["res.partner"].create(
            {"name": "Test partner 1", "email": "test@mail.com"}
        )
        cls.partner_without_mail = cls.env["res.partner"].create(
            {
                "name": "Test partner 2",
            }
        )

        cls.first_eligible_invoice = cls.init_invoice(
            "out_invoice", partner=cls.partner_with_email, amounts=[20], post=True
        )
        cls.second_eligible_invoice = cls.init_invoice(
            "out_invoice", partner=cls.partner_with_email, amounts=[20], post=True
        )
        cls.invoice_without_mail = cls.init_invoice(
            "out_invoice", partner=cls.partner_without_mail, amounts=[20], post=True
        )
        cls.invoice_in_progress = cls.init_invoice(
            "out_invoice", partner=cls.partner_with_email, amounts=[20], post=False
        )
        cls.invoice_in_progress.sending_in_progress = True
        cls.invoice_in_progress.action_post()

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
