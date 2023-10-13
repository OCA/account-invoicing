# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from .. import post_init_hook


class TestInvoiceRefundLinkBase(TransactionCase):
    refund_method = "refund"

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
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        default_line_account = cls.env["account.account"].create(
            {
                "name": "TESTACC",
                "code": "TESTACC",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_other_income"
                ).id,
                "deprecated": False,
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Journal 1",
                "code": "J1",
                "type": "sale",
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.invoice_lines = [
            (
                0,
                False,
                {
                    "name": "Test description #1",
                    "account_id": default_line_account.id,
                    "quantity": 1.0,
                    "price_unit": 100.0,
                },
            ),
            (
                0,
                False,
                {
                    "name": "Test description #2",
                    "account_id": default_line_account.id,
                    "quantity": 2.0,
                    "price_unit": 25.0,
                },
            ),
        ]
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": cls.invoice_lines,
            }
        )
        cls.invoice.action_post()
        cls.refund_reason = "The refund reason"
        cls.env["account.move.reversal"].with_context(
            active_ids=cls.invoice.ids, active_model="account.move"
        ).create(
            {
                "refund_method": cls.refund_method,
                "reason": cls.refund_reason,
                "journal_id": cls.journal.id,
            }
        ).reverse_moves()

    def _test_refund_link(self):
        self.assertTrue(self.invoice.refund_invoice_ids)
        refund = self.invoice.refund_invoice_ids[0]
        ref = "Reversal of: {}, {}".format(self.invoice.name, self.refund_reason)
        self.assertEqual(refund.ref, ref)
        self.assertEqual(len(self.invoice.invoice_line_ids), len(self.invoice_lines))
        self.assertEqual(len(refund.invoice_line_ids), len(self.invoice_lines))
        self.assertTrue(refund.invoice_line_ids[0].origin_line_id)
        self.assertEqual(
            self.invoice.invoice_line_ids[0], refund.invoice_line_ids[0].origin_line_id
        )
        self.assertTrue(refund.invoice_line_ids[1].origin_line_id)
        self.assertEqual(
            self.invoice.invoice_line_ids[1], refund.invoice_line_ids[1].origin_line_id
        )


class TestInvoiceRefundLink(TestInvoiceRefundLinkBase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceRefundLink, cls).setUpClass()

    def test_post_init_hook(self):
        self.assertTrue(self.invoice.refund_invoice_ids)
        refund = self.invoice.refund_invoice_ids[0]
        refund.invoice_line_ids.write({"origin_line_id": False})
        self.assertFalse(refund.mapped("invoice_line_ids.origin_line_id"))
        post_init_hook(self.env.cr, None)
        self.refund_reason = "The refund reason"
        self._test_refund_link()

    def test_refund_link(self):
        self._test_refund_link()

    def test_invoice_copy(self):
        refund = self.invoice.refund_invoice_ids[0]
        self.invoice.copy()
        self.assertEqual(
            refund.invoice_line_ids.mapped("origin_line_id"),
            self.invoice.invoice_line_ids,
        )

    def test_refund_copy(self):
        refund = self.invoice.refund_invoice_ids[0]
        refund.copy()
        self.assertEqual(
            self.invoice.invoice_line_ids.mapped("refund_line_ids"),
            refund.invoice_line_ids,
        )


class TestInvoiceRefundCancelLink(TestInvoiceRefundLinkBase):
    refund_method = "cancel"

    def test_refund_link(self):
        self._test_refund_link()


class TestInvoiceRefundModifyLink(TestInvoiceRefundLinkBase):
    refund_method = "modify"

    def test_refund_link(self):
        self._test_refund_link()
