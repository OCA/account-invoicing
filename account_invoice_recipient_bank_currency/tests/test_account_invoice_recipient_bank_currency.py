# Copyright 2024 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAccountInvoiceRecipientBankCurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_move_model = cls.env["account.move"]
        cls.journal_model = cls.env["account.journal"]
        cls.partner_model = cls.env["res.partner"]
        cls.partner_bank_model = cls.env["res.partner.bank"]
        cls.company = cls.env.company

        cls.journal = cls.journal_model.create(
            {
                "name": "Test Journal",
                "code": "tSAL",
                "type": "sale",
                "company_id": cls.company.id,
            }
        )
        cls.partner = cls.partner_model.create(
            {
                "name": "Test Partner",
                "company_id": cls.company.id,
            }
        )

        cls.bank_acc1 = cls.partner_bank_model.create(
            {
                "acc_number": "1234567890",
                "partner_id": cls.partner.id,
                "currency_id": cls.env.ref("base.USD").id,
                "sequence": 1,
            }
        )
        cls.bank_acc2 = cls.partner_bank_model.create(
            {
                "acc_number": "0987654321",
                "partner_id": cls.partner.id,
                "currency_id": cls.env.ref("base.EUR").id,
                "sequence": 2,
            }
        )
        cls.bank_acc3 = cls.partner_bank_model.create(
            {
                "acc_number": "1112223334",
                "partner_id": cls.partner.id,
                "currency_id": cls.env.ref("base.USD").id,
                "sequence": 3,
            }
        )
        cls.bank_acc4 = cls.partner_bank_model.create(
            {
                "acc_number": "9998887776",
                "partner_id": cls.partner.id,
                "currency_id": cls.env.ref("base.EUR").id,
                "sequence": 4,
            }
        )

    def test_account_invoice_recipient_bank_currency(self):
        invoice_USD = self.account_move_model.create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "date": fields.Date.today(),
                "currency_id": self.env.ref("base.USD").id,
            }
        )
        invoice_EUR = self.account_move_model.create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "date": fields.Date.today(),
                "currency_id": self.env.ref("base.EUR").id,
            }
        )
        invoice_DKK = self.account_move_model.create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "date": fields.Date.today(),
                "currency_id": self.env.ref("base.DKK").id,
            }
        )

        self.assertEqual(invoice_USD.partner_bank_id, self.bank_acc1)
        self.assertEqual(invoice_EUR.partner_bank_id, self.bank_acc2)
        self.assertEqual(invoice_DKK.partner_bank_id, self.bank_acc1)

        self.bank_acc4.sequence = 1
        self.bank_acc3.sequence = 2
        self.bank_acc2.sequence = 3
        self.bank_acc1.sequence = 4
        invoice_USD._compute_partner_bank_id()
        invoice_EUR._compute_partner_bank_id()
        invoice_DKK._compute_partner_bank_id()

        self.assertEqual(invoice_USD.partner_bank_id, self.bank_acc3)
        self.assertEqual(invoice_EUR.partner_bank_id, self.bank_acc4)
        self.assertEqual(invoice_DKK.partner_bank_id, self.bank_acc1)

        self.bank_acc1.unlink()
        self.bank_acc3.unlink()
        invoice_USD._compute_partner_bank_id()
        invoice_EUR._compute_partner_bank_id()
        invoice_DKK._compute_partner_bank_id()

        self.assertEqual(invoice_USD.partner_bank_id, self.bank_acc4)
        self.assertEqual(invoice_EUR.partner_bank_id, self.bank_acc4)
        self.assertEqual(invoice_DKK.partner_bank_id, self.bank_acc4)
