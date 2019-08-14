# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountInvoice(SavepointCase):
    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        account_receivable_type = self.env.ref(
            'account.data_account_type_receivable'
        )
        self.account_receivable = self.env['account.account'].create(
            {
                'name': 'Partner Receivable',
                'code': 'RCV00',
                'user_type_id': account_receivable_type.id,
                'reconcile': True,
            }
        )
        self.account_receivable_brand_default = self.env[
            'account.account'
        ].create(
            {
                'name': 'Receivable Brand Default',
                'code': 'RCV01',
                'user_type_id': account_receivable_type.id,
                'reconcile': True,
            }
        )
        self.account_receivable_partner_brand_default = self.env[
            'account.account'
        ].create(
            {
                'name': 'Receivable Partner Brand Default',
                'code': 'RCV02',
                'user_type_id': account_receivable_type.id,
                'reconcile': True,
            }
        )
        self.partner_id = self.env.ref('base.res_partner_12')
        self.partner_id.property_account_receivable_id = (
            self.account_receivable
        )
        self.invoice = self.env['account.invoice'].create(
            {'partner_id': self.partner_id.id, 'type': 'out_invoice'}
        )
        type_revenue = self.env.ref('account.data_account_type_revenue')
        self.account_revenue = self.env['account.account'].create(
            {
                'name': 'Test sale',
                'code': 'XX_700',
                'user_type_id': type_revenue.id,
            }
        )
        product = self.env.ref('product.product_product_4')
        self.env['account.invoice.line'].create(
            {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': 42,
                'invoice_id': self.invoice.id,
                'name': 'something',
                'account_id': self.account_revenue.id,
            }
        )
        self.brand_id = self.env['res.partner'].create(
            {'name': 'Brand', 'type': 'brand'}
        )

    def test_on_change_product_id(self):
        self.invoice._onchange_partner_id()
        self.assertEqual(self.invoice.account_id, self.account_receivable)
        partner_account_brand = self.env['res.partner.account.brand'].create(
            {
                'partner_id': False,
                'account_id': self.account_receivable_brand_default.id,
                'brand_id': self.brand_id.id,
                'account_type': 'receivable',
            }
        )
        self.invoice._onchange_partner_id()
        self.assertEqual(self.invoice.account_id, self.account_receivable)
        self.invoice.brand_id = self.brand_id
        self.invoice._onchange_partner_id()
        self.assertEqual(
            self.invoice.account_id, self.account_receivable_brand_default
        )
        partner_account_brand.update(
            {
                'partner_id': self.partner_id.id,
                'account_id': self.account_receivable_partner_brand_default.id,
            }
        )
        self.invoice._onchange_partner_id()
        self.assertEqual(
            self.invoice.account_id,
            self.account_receivable_partner_brand_default,
        )
        invoice = self.env['account.invoice'].create(
            {
                'partner_id': self.partner_id.id,
                'brand_id': self.brand_id.id,
                'type': 'out_invoice',
            }
        )
        self.assertEqual(
            invoice.account_id,
            self.account_receivable_partner_brand_default,
        )
