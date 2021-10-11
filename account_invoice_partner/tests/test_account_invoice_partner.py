# Copyright 2015-2017 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountInvoiceParner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # MODELS
        cls.AccountMove = cls.env["account.move"]
        cls.ResPartner = cls.env["res.partner"]
        cls.AccountAccount = cls.env["account.account"]
        cls.AccountJournal = cls.env["account.journal"]

        # INSTANCE
        partners = cls.ResPartner.search(
            [("type", "!=", "invoice"), ("child_ids", "=", False)], limit=2
        )
        cls.partner = partners[0]
        cls.partner_2 = partners[1]

        # invoice
        journal = cls.AccountJournal.create(
            {"name": "Purchase Journal - Test", "code": "STPJ", "type": "purchase"}
        )
        invoice_vals = {
            "name": "TEST",
            "move_type": "in_invoice",
            "partner_id": cls.partner.id,
            "journal_id": journal.id,
        }
        cls.invoice = cls.AccountMove.create(invoice_vals)

    def test_0(self):
        # these partners are differents
        self.assertNotEqual(self.partner, self.partner_2)

        # partner is define in invoice
        self.assertEqual(self.invoice.partner_id, self.partner)

        # partner has no address defined for invoice
        self.invoice._onchange_partner_id()
        self.assertEqual(self.invoice.partner_id, self.partner)

        # change partner type to define partner invoice address
        self.partner_2.write({"type": "invoice"})
        self.partner.write({"child_ids": [(6, 0, self.partner_2.ids)]})
        self.assertIn(self.partner_2, self.partner.child_ids)

        # test onchange function
        self.invoice._onchange_partner_id()
        self.assertEqual(self.invoice.partner_id, self.partner_2)
