# Copyright 2020 ForgeFlow S.L.
# Copyright 2021 Onestein (<https://www.onestein.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.exceptions import ValidationError


class TestInvoiceTierValidation(AccountingTestCase):
    def setUp(self):
        super().setUp()
        self.tier_definition = self.env['tier.definition']
        self.test_user_1 = self.env['res.users'].create({
            'name': 'John',
            'login': 'test1',
            'groups_id': [(6, 0, self.env.ref('base.group_system').ids)],
            'email': "email@example.com",
        })
        type_receivable = self.env.ref('account.data_account_type_receivable')
        type_revenue = self.env.ref('account.data_account_type_revenue')
        self.account_receivable = self.env['account.account'].search([
            ('user_type_id', '=', type_receivable.id)
        ], limit=1)
        self.account_revenue = self.env['account.account'].search([
            ('user_type_id', '=', type_revenue.id)
        ], limit=1)
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref("base.res_partner_2").id,
            'currency_id': self.env.ref('base.EUR').id,
            'name': 'invoice name',
            'account_id': self.account_receivable.id,
            'type': 'out_invoice',
        })
        self.env['account.invoice.line'].create({
            'product_id': self.env.ref("product.product_product_4").id,
            'quantity': 1,
            'price_unit': 100.0,
            'invoice_id': self.invoice.id,
            'name': 'something',
            'account_id': self.account_revenue.id,
            'invoice_line_tax_ids': False
        })
        self.invoice._onchange_invoice_line_ids()

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            'account.invoice',
            self.tier_definition._get_tier_validation_model_names()
        )

    def test_account_invoice_tier_validation(self):
        invoice = self.invoice.with_context(force_check_tier_validation=True)
        with self.assertRaises(ValidationError):
            invoice.action_invoice_open()
        invoice.request_validation()
        invoice.sudo(self.test_user_1).validate_tier()
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, "open")
