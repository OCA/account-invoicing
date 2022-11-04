from odoo.tests.common import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountRefundPaymentTerm(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # this is already done by super class but ensure it remains the same
        cls.partner_a.property_payment_term_id = cls.pay_terms_a.id
        cls.partner_b.property_payment_term_id = cls.pay_terms_b.id
        # different refund payment terms
        cls.partner_a.property_refund_payment_term_id = cls.pay_terms_b.id
        cls.partner_b.property_refund_payment_term_id = None

    def test_create_out_refund(self):
        with Form(
            self.env["account.move"].with_context(default_move_type="out_refund")
        ) as move_form:
            move_form.partner_id = self.partner_a
            invoice = move_form.save()

        self.assertEqual(invoice.invoice_payment_term_id, self.pay_terms_b)

    def test_update_out_refund_on_change_partner(self):
        with Form(
            self.env["account.move"].with_context(default_move_type="out_refund")
        ) as move_form:
            move_form.partner_id = self.partner_a
            invoice = move_form.save()

        with Form(invoice) as move_form:
            move_form.partner_id = self.partner_b

        self.assertFalse(invoice.invoice_payment_term_id)

    def test_commercial_partner(self):
        # in case partner_b become child of partner_a
        # property_refund_payment_term_id must be synced with its
        # parent: partner_a
        self.partner_b.write({"parent_id": self.partner_a.id})
        self.assertEqual(
            self.partner_b.property_refund_payment_term_id, self.pay_terms_b
        )
