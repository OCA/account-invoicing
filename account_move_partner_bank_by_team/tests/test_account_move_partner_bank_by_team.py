# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountPartnerBankSource(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.crm_team_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "11122233",
                "partner_id": cls.company.partner_id.id,
                "company_id": cls.company.id,
                "allow_out_payment": True,
            }
        )
        cls.sales_team = cls.env["crm.team"].create(
            {
                "name": "Sales Team",
                "company_id": cls.company.id,
                "bank_account_id": cls.crm_team_bank.id,
            }
        )

    def creat_invoice(self, partner):
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "team_id": self.sales_team.id,
            }
        )

    def test_account_move_partner_bank(self):
        self.company.account_move_bank_source_ids = False
        move = self.creat_invoice(self.partner)
        self.assertNotEqual(move.partner_bank_id, self.crm_team_bank)
        self.env["bank.account.source"].create(
            {
                "company_id": self.company.id,
                "sequence": 10,
                "source_model_id": self.env.ref("account.model_account_move").id,
                "bank_field_path": "team_id.bank_account_id",
            }
        )
        move = self.creat_invoice(self.partner)
        self.assertEqual(move.partner_bank_id, self.crm_team_bank)
