#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests


class TestFiscalPosition(tests.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner_model = cls.env["res.partner"]
        cls.fiscal_pos_model = cls.env["account.fiscal.position"]

        cls.receipts_fiscal_position = cls.fiscal_pos_model.create(
            {
                "name": "receipts fiscal position",
                "receipts": True,
                "company_id": cls.env.company.id,
            }
        )
        cls.no_receipts_fiscal_position = cls.fiscal_pos_model.create(
            {
                "name": "no receipts fiscal position",
                "receipts": False,
                "company_id": cls.env.company.id,
            }
        )
        cls.receipts_partner = partner_model.create(
            {
                "name": "Receipts partner",
                "use_receipts": True,
                "property_account_position_id": cls.receipts_fiscal_position.id,
            }
        )
        cls.no_receipts_partner = partner_model.create(
            {
                "name": "No receipts partner",
                "use_receipts": False,
                "property_account_position_id": cls.no_receipts_fiscal_position.id,
            }
        )

    def test_get_receipts_fiscal_pos(self):
        """Test that get_receipts_fiscal_pos gets a receipts
        fiscal position"""
        receipts_fiscal_pos = self.fiscal_pos_model.get_receipts_fiscal_pos()
        self.assertTrue(receipts_fiscal_pos.receipts)

    def test_receipts_partner_onchange(self):
        """Test onchange in partner."""
        # If the partner uses receipts,
        # the fiscal position must have the flag receipts
        self.receipts_partner.onchange_use_receipts()
        self.assertTrue(self.receipts_partner.property_account_position_id.receipts)

        # If the partner does not use receipts
        # and it already has a fiscal position that is
        # receipts, it must be removed
        self.no_receipts_partner.update(
            {"property_account_position_id": self.receipts_fiscal_position.id}
        )
        self.no_receipts_partner.onchange_use_receipts()
        self.assertFalse(self.no_receipts_partner.property_account_position_id)

        # If the partner does not use receipts
        # and it already has a fiscal position that is
        # not receipts, it must not be removed
        self.no_receipts_partner.write(
            {"property_account_position_id": self.no_receipts_fiscal_position.id}
        )
        self.no_receipts_partner.onchange_use_receipts()
        self.assertEqual(
            self.no_receipts_partner.property_account_position_id,
            self.no_receipts_fiscal_position,
        )
