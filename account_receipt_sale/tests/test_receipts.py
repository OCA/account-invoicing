# Copyright 2018 Simone Rubino
# Copyright 2022 Lorenzo Battistini

from odoo.addons.account_receipt_journal.tests.test_receipts \
    import TestReceipts
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestReceiptsSale(TestReceipts):

    def setUp(self):
        super(TestReceiptsSale, self).setUp()
        partner_model = self.env['res.partner']
        self.fiscal_pos_model = self.env['account.fiscal.position']
        self.sale_model = self.env['sale.order']
        self.receipts_fiscal_position = self.fiscal_pos_model.create({
            'name': 'receipts fiscal position',
            'receipts': True,
            'company_id': self.env.user.company_id.id
        })
        self.no_receipts_fiscal_position = self.fiscal_pos_model.create({
            'name': 'no receipts fiscal position',
            'receipts': False,
            'company_id': self.env.user.company_id.id
        })
        self.receipts_partner = partner_model.create({
            'name': 'Receipts partner',
            'use_receipts': True,
            'property_account_position_id': self.receipts_fiscal_position.id
        })
        self.no_receipts_partner = partner_model.create({
            'name': 'No receipts partner',
            'use_receipts': False,
            'property_account_position_id': self.no_receipts_fiscal_position.id
        })

    def test_get_receipts_fiscal_pos(self):
        """ Test that get_receipts_fiscal_pos gets a receipts
        fiscal position"""
        receipts_fiscal_pos = self.fiscal_pos_model.get_receipts_fiscal_pos()
        self.assertTrue(receipts_fiscal_pos.receipts)

    def test_receipts_partner_onchange(self):
        """ Test onchange in partner. """
        # If the partner uses receipts,
        # the fiscal position must have the flag receipts
        self.receipts_partner.onchange_use_receipts()
        self.assertTrue(self.receipts_partner
                        .property_account_position_id.receipts)

        # If the partner does not use receipts
        # and it already has a fiscal position that is
        # receipts, it must be removed
        self.no_receipts_partner.write({
            'property_account_position_id': self.receipts_fiscal_position.id})
        self.no_receipts_partner.onchange_use_receipts()
        self.assertFalse(
            self.no_receipts_partner.property_account_position_id)

        # If the partner does not use receipts
        # and it already has a fiscal position that is
        # not receipts, it must not be removed
        self.no_receipts_partner.write({
            'property_account_position_id': self.no_receipts_fiscal_position.id})
        self.no_receipts_partner.onchange_use_receipts()
        self.assertEqual(
            self.no_receipts_partner.property_account_position_id,
            self.no_receipts_fiscal_position)

    def test_order_creation(self):
        order_no_receipts = self.sale_model.create({
            "partner_id": self.no_receipts_partner.id,
            "fiscal_position_id": self.no_receipts_fiscal_position.id,
        })
        self.assertFalse(order_no_receipts.receipts)
        order_receipts = self.sale_model.create({
            "partner_id": self.no_receipts_partner.id,
            "fiscal_position_id": self.receipts_fiscal_position.id,
        })
        self.assertTrue(order_receipts.receipts)

        # testing write
        order_no_receipts.fiscal_position_id = self.receipts_fiscal_position.id
        self.assertTrue(order_no_receipts.receipts)
