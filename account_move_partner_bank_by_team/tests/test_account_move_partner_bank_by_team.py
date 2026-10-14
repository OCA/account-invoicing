# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPartnerBankSelection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.partner_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "99990000",
                "partner_id": cls.company.partner_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.crm_team_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "11122233",
                "partner_id": cls.company.partner_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.sales_team = cls.env["crm.team"].create(
            {
                "name": "Sales Team",
                "company_id": cls.company.id,
                "bank_account_id": cls.crm_team_bank.id,
            }
        )

    def test_account_move_partner_bank(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "team_id": self.sales_team.id,
            }
        )
        self.assertEqual(move.partner_bank_id, self.crm_team_bank)
        self.sales_team.bank_account_id = False
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "team_id": self.sales_team.id,
            }
        )
        self.assertNotEqual(move.partner_bank_id, self.crm_team_bank)
        self.assertEqual(move.partner_bank_id, self.partner_bank)
