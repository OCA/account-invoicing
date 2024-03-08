# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceAlternateCommercialPartner(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.in_invoice = cls.init_invoice("in_invoice", products=cls.product_b)
        cls.out_invoice = cls.init_invoice("out_invoice", products=cls.product_a)
        cls.in_invoice_02 = cls.init_invoice("in_invoice", products=cls.product_a)
        cls.out_invoice_02 = cls.init_invoice("out_invoice", products=cls.product_b)
        cls.alternate_partner = cls.env["res.partner"].create(
            {"name": "Alternate Payer"}
        )
        cls.payment_method_manual_out = cls.env.ref(
            "account.account_payment_method_manual_out"
        )
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        cls.bank_journal_euro = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        cls.bank_account = cls.env["account.account"].create(
            {
                "name": "Demo Bank account",
                "code": "demo_bank_account",
                "user_type_id": cls.env.ref("account.data_account_type_liquidity").id,
            }
        )

    def test_01_onchange_out_invoice(self):
        with Form(self.out_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        self.assertEqual(
            self.out_invoice.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
            ).mapped("partner_id"),
            self.alternate_partner,
        )
        self.assertEqual(
            self.out_invoice.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type
                not in ("receivable", "payable")
            ).mapped("partner_id"),
            self.out_invoice.partner_id,
        )
        self.assertEqual(
            self.out_invoice.bank_partner_id, self.out_invoice.company_id.partner_id
        )

    def test_01_1_post_out_invoice(self):
        with Form(self.out_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
            self.out_invoice_posted = form.save()
        self.out_invoice_posted.action_post()
        self.assertEqual(
            self.out_invoice_posted.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
            ).mapped("partner_id"),
            self.alternate_partner,
        )
        self.assertEqual(
            self.out_invoice_posted.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type
                not in ("receivable", "payable")
            ).mapped("partner_id"),
            self.out_invoice_posted.partner_id,
        )
        self.assertEqual(
            self.out_invoice_posted.bank_partner_id,
            self.out_invoice_posted.company_id.partner_id,
        )

    def test_02_onchange_in_invoice(self):
        with Form(self.in_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        self.assertEqual(
            self.in_invoice.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
            ).mapped("partner_id"),
            self.alternate_partner,
        )
        self.assertEqual(
            self.in_invoice.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type
                not in ("receivable", "payable")
            ).mapped("partner_id"),
            self.out_invoice.partner_id,
        )
        self.assertEqual(self.in_invoice.bank_partner_id, self.alternate_partner)

    def test_02_1_post_in_invoice(self):
        with Form(self.in_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
            self.in_invoice_posted = form.save()
        self.in_invoice_posted.action_post()
        self.assertEqual(
            self.in_invoice_posted.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
            ).mapped("partner_id"),
            self.alternate_partner,
        )
        self.assertEqual(
            self.in_invoice_posted.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type
                not in ("receivable", "payable")
            ).mapped("partner_id"),
            self.out_invoice.partner_id,
        )
        self.assertEqual(self.in_invoice_posted.bank_partner_id, self.alternate_partner)

    def test_03_payment_out_invoice(self):
        with Form(self.out_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        self.out_invoice._post()
        records = self.out_invoice
        ctx = {"active_model": records._name, "active_ids": records.ids}
        payment = (
            self.env["account.payment"]
            .with_context(**ctx)
            .create(
                {
                    "payment_method_id": self.payment_method_manual_out.id,
                    "journal_id": self.bank_journal_euro.id,
                }
            )
        )
        self.assertEqual(payment.partner_id, self.alternate_partner)

    def test_04_payment_in_invoice(self):
        with Form(self.in_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        self.in_invoice._post()
        records = self.in_invoice
        ctx = {"active_model": records._name, "active_ids": records.ids}
        payment = (
            self.env["account.payment"]
            .with_context(**ctx)
            .create(
                {
                    "payment_method_id": self.payment_method_manual_in.id,
                    "journal_id": self.bank_journal_euro.id,
                }
            )
        )
        self.assertEqual(payment.partner_id, self.alternate_partner)

    def test_05_payment_out_invoices(self):
        with Form(self.out_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        self.out_invoice._post()
        with Form(self.out_invoice_02) as form:
            form.alternate_payer_id = self.alternate_partner
        self.out_invoice_02._post()
        records = self.out_invoice | self.out_invoice_02
        ctx = {"active_model": records._name, "active_ids": records.ids}
        payments = (
            self.env["account.payment"]
            .with_context(**ctx)
            .create(
                {
                    "payment_method_id": self.payment_method_manual_out.id,
                    "journal_id": self.bank_journal_euro.id,
                }
            )
        )
        for payment in payments:
            self.assertEqual(payment.partner_id, self.alternate_partner)

    def test_06_payment_in_invoices(self):
        with Form(self.in_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        self.in_invoice._post()
        with Form(self.in_invoice_02) as form:
            form.alternate_payer_id = self.alternate_partner
        self.in_invoice_02._post()
        records = self.in_invoice | self.in_invoice_02
        ctx = {"active_model": records._name, "active_ids": records.ids}
        payments = (
            self.env["account.payment"]
            .with_context(**ctx)
            .create(
                {
                    "payment_method_id": self.payment_method_manual_out.id,
                    "journal_id": self.bank_journal_euro.id,
                }
            )
        )
        for payment in payments:
            self.assertEqual(payment.partner_id, self.alternate_partner)

    def test_07_payment_widget_in_invoices(self):
        with Form(self.in_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        line = self.in_invoice.line_ids.filtered(
            lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
        )
        payment_move = self.env["account.move"].create(
            {
                "journal_id": self.bank_journal_euro.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": line.account_id.id,
                            "partner_id": line.partner_id.id,
                            "debit": line.credit,
                            "credit": line.debit,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.bank_account.id,
                            "debit": line.debit,
                            "credit": line.credit,
                        },
                    ),
                ],
            }
        )
        payment_move.action_post()
        self.assertFalse(self.in_invoice.invoice_has_outstanding)
        self.in_invoice._post()
        self.in_invoice.refresh()
        self.assertTrue(self.in_invoice.invoice_has_outstanding)
        self.in_invoice.write({"payment_state": "paid"})
        self.in_invoice.refresh()
        self.assertFalse(self.in_invoice.invoice_has_outstanding)

    def test_08_payment_widget_out_invoices(self):
        with Form(self.out_invoice) as form:
            form.alternate_payer_id = self.alternate_partner
        line = self.out_invoice.line_ids.filtered(
            lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
        )
        payment_move = self.env["account.move"].create(
            {
                "journal_id": self.bank_journal_euro.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": line.account_id.id,
                            "partner_id": line.partner_id.id,
                            "debit": line.credit,
                            "credit": line.debit,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.bank_account.id,
                            "debit": line.debit,
                            "credit": line.credit,
                        },
                    ),
                ],
            }
        )
        payment_move.action_post()
        self.assertFalse(self.out_invoice.invoice_has_outstanding)
        self.out_invoice._post()
        self.out_invoice.refresh()
        self.assertTrue(self.out_invoice.invoice_has_outstanding)
        self.out_invoice.write({"payment_state": "paid"})
        self.out_invoice.refresh()
        self.assertFalse(self.out_invoice.invoice_has_outstanding)
