# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestAccountDebitNote(TransactionCase):
    def setUp(self):
        super(TestAccountDebitNote, self).setUp()
        self.AccountMove = self.env["account.move"]
        self.AccountJournal = self.env["account.journal"]
        self.Wizard = self.env["account.move.debitnote"]
        self.test_partner = self.env.ref("base.res_partner_12")
        self.test_product = self.env.ref("product.product_product_7")
        self.test_customer_debitnote = self.env["account.journal"].create(
            {
                "name": "TEST DEBITNOTE",
                "type": "sale",
                "code": "TINV",
                "debitnote_sequence": True,
            }
        )

    def call_invoice_debit_note(self, invoice):
        vals = {"date": date.today() + relativedelta(days=1), "reason": "Test"}
        wiz_id = self.Wizard.with_context(
            active_model="account.move", active_ids=[invoice.id]
        ).create(vals)
        wiz_id.invoice_debitnote()

    def test_1_account_debitnote(self):
        """I create invoice, validate it, and create debit note. I expect,
        - Invoice is open
        - Debit note is created
        """
        vals = {
            "partner_id": self.test_partner.id,
            "type": "out_invoice",
            "journal_id": self.test_customer_debitnote.id,
            "invoice_line_ids": [
                [0, 0, {"product_id": self.test_product.id, "quantity": 2.0}]
            ],
        }
        invoice = self.AccountMove.create(vals)
        invoice.post()
        self.assertEqual(invoice.state, "posted")
        # Create Debit Note
        self.call_invoice_debit_note(invoice)
        debit = self.env["account.move"].search([("debit_move_id", "=", invoice.id)])
        debit.journal_id.write(
            {
                "debitnote_sequence_id": True,
                "debitnote_sequence_number_next": 200,
                "debitnote_sequence": True,
            }
        )
        with self.assertRaises(UserError):
            debit.post()
        debit.write({"date": date.today()})
        debit.post()
        self.assertEqual(debit.state, "posted")

    def test_2_Error(self):
        """Create debit note in Credit note and Refund. I expect,
        - ValidationError
        """
        vals = {
            "partner_id": self.test_partner.id,
            "type": "out_invoice",
            "journal_id": self.test_customer_debitnote.id,
            "invoice_line_ids": [
                [0, 0, {"product_id": self.test_product.id, "quantity": 2.0}]
            ],
        }
        invoice = self.AccountMove.create(vals)
        invoice.post()
        self.call_invoice_debit_note(invoice)
        debit = self.env["account.move"].search([("debit_move_id", "=", invoice.id)])
        with self.assertRaises(UserError):
            debit.post()
        debit.journal_id.write({"debitnote_sequence_id": False})
        debit.write({"date": date.today()})
        # UserError define sequence
        with self.assertRaises(UserError):
            debit.post()
        debit.journal_id.write(
            {
                "debitnote_sequence_id": True,
                "debitnote_sequence_number_next": 200,
                "debitnote_sequence": True,
            }
        )
        debit.write({"date": date.today()})
        # Create debitnote from debitnote
        with self.assertRaises(ValidationError):
            self.call_invoice_debit_note(debit)
        # Call wizard without invoice
        vals = {"date": date.today(), "reason": "Test"}
        wiz_id = self.Wizard.with_context(
            active_model="account.move", active_ids=[]
        ).create(vals)
        wiz_id.invoice_debitnote()

    def test_3_compute_field(self):
        vals = {
            "partner_id": self.test_partner.id,
            "type": "out_invoice",
            "journal_id": self.test_customer_debitnote.id,
            "invoice_line_ids": [
                [0, 0, {"product_id": self.test_product.id, "quantity": 2.0}]
            ],
        }
        invoice = self.AccountMove.create(vals)
        invoice.post()
        vals = {
            "partner_id": self.test_partner.id,
            "type": "out_invoice",
            "journal_id": self.test_customer_debitnote.id,
            "invoice_line_ids": [
                [0, 0, {"product_id": self.test_product.id, "quantity": 2.0}]
            ],
        }
        invoice_2 = self.AccountMove.create(vals)
        invoice_2.post()
        vals = {"date": date.today() + relativedelta(days=1), "reason": "Test"}
        wiz_id = self.Wizard.with_context(
            active_model="account.move", active_ids=[invoice.id, invoice_2.id]
        ).create(vals)
        # Compute: residual, currency_id, move_type
        wiz_id._compute_from_moves()
        wiz_id.invoice_debitnote()
        debit = self.env["account.move"].search([("debit_move_id", "=", invoice.id)])
        debit.journal_id.write(
            {
                "debitnote_sequence_id": True,
                "debitnote_sequence_number_next": 200,
                "debitnote_sequence": True,
            }
        )
        # Compute: debitnote_sequence_number_next
        debit.journal_id._compute_debitnote_seq_number_next()
        debit.journal_id.update({"debitnote_sequence": False})
        debit.journal_id._compute_debitnote_seq_number_next()
