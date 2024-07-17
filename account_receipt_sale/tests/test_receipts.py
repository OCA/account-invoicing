# Copyright 2018 Simone Rubino
# Copyright 2022 Lorenzo Battistini
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account_receipt_journal.tests.test_receipts import TestReceipts


@tagged("post_install", "-at_install")
class TestReceiptsSale(TestReceipts):
    def setUp(self):
        super(TestReceiptsSale, self).setUp()
        partner_model = self.env["res.partner"]
        self.fiscal_pos_model = self.env["account.fiscal.position"]
        self.sale_model = self.env["sale.order"]
        self.receipts_fiscal_position = self.fiscal_pos_model.create(
            {
                "name": "receipts fiscal position",
                "receipts": True,
                "company_id": self.env.user.company_id.id,
            }
        )
        self.no_receipts_fiscal_position = self.fiscal_pos_model.create(
            {
                "name": "no receipts fiscal position",
                "receipts": False,
                "company_id": self.env.user.company_id.id,
            }
        )
        self.no_receipts_partner = partner_model.create(
            {
                "name": "No receipts partner",
                "use_receipts": False,
                "property_account_position_id": self.no_receipts_fiscal_position.id,
            }
        )

    def test_order_creation(self):
        order_no_receipts = self.sale_model.create(
            {
                "partner_id": self.no_receipts_partner.id,
                "fiscal_position_id": self.no_receipts_fiscal_position.id,
            }
        )
        self.assertFalse(order_no_receipts.receipts)
        order_receipts = self.sale_model.create(
            {
                "partner_id": self.no_receipts_partner.id,
                "fiscal_position_id": self.receipts_fiscal_position.id,
            }
        )
        self.assertTrue(order_receipts.receipts)

        # testing write
        order_no_receipts.fiscal_position_id = self.receipts_fiscal_position.id
        self.assertTrue(order_no_receipts.receipts)
