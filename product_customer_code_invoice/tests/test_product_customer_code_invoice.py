# -*- coding: utf-8 -*-
# © 2017 Roberto Onnis - innoviu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.tests.common import TransactionCase


class TestProductCustomerCodeInvoice(TransactionCase):

    def setUp(self):
        super(TestProductCustomerCodeInvoice, self).setUp()
        # Useful models
        self.ProductCustomerCode = self.env['product.customer.code']
        self.AccountInvoice = self.env['account.invoice']

    def test_00_invoice_customer_code(self):
        self.partner_id = self.env.ref('base.res_partner_3')
        self.product_id = self.env.ref('product.product_product_11')
        self.account_id = self.env['account.account'].search(
            [
                ('user_type_id',
                 '=',
                 self.env.ref('account.data_account_type_revenue').id)
            ], limit=1).id

        self.ProductCustomerCode.create(
            {
                'product_name': self.product_id.name +
                '4' + self.partner_id.name,
                'product_code': 'codeA01',
                'product_id': self.product_id.id,
                'partner_id': self.partner_id.id
            }
        )
        inv_vals = {
            'partner_id': self.partner_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': self.product_id.name,
                    'product_id': self.product_id.id,
                    'quantity': 1.0,
                    'account_id': self.account_id,
                    'price_unit': 100.00,
                }),
            ],
        }
        self.inv = self.AccountInvoice.create(inv_vals)
        self.assertTrue(self.inv, 'No invoice created')
        self.assertTrue(
            self.inv.invoice_line_ids and self.inv.invoice_line_ids[0],
            'No invoice line created')
        self.assertEqual(
            self.inv.invoice_line_ids[0].product_customer_code, 'codeA01',
            'Invoice line customer code should be "codeA01"')
