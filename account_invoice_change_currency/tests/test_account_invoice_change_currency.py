# Copyright 2018 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
import odoo.tests.common as common


class TestAccountInvoiceChangeCurrency(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceChangeCurrency, self).setUp()

        res_users_account_manager = self.env.ref(
            'account.group_account_manager')
        self.manager = self.env['res.users'].with_context({
            'no_reset_password': True}).create(dict(
                name="Adviser",
                company_id=self.env.ref('base.main_company').id,
                login="fm",
                email="accountmanager@yourcompany.com",
                groups_id=[(6, 0, [
                    res_users_account_manager.id])]
            ))

        # Needed to create invoice
        self.account_type1 = self.env['account.account.type'].\
            create({'name': 'acc type test 1',
                    'type': 'receivable',
                    'include_initial_balance': True})
        self.account_type2 = self.env['account.account.type']. \
            create({'name': 'acc type test 2',
                    'type': 'other',
                    'include_initial_balance': True})
        self.account_account = self.env['account.account'].\
            create({'name': 'acc test',
                    'code': 'X2020',
                    'user_type_id': self.account_type1.id,
                    'reconcile': True})
        self.account_account_line = self.env['account.account']. \
            create({'name': 'acc inv line test',
                    'code': 'X2021',
                    'user_type_id': self.account_type2.id,
                    'reconcile': True})
        self.sequence = self.env['ir.sequence'].create(
            {'name': 'Journal Sale',
             'prefix': 'SALE', 'padding': 6,
             'company_id': self.env.ref("base.main_company").id})
        self.account_journal_sale = self.env['account.journal']\
            .create({'name': 'Sale journal',
                     'code': 'SALE',
                     'type': 'sale',
                     'sequence_id': self.sequence.id})
        self.product_1 = self.env['product.product'].create(
            {'name': 'Product 1'})
        self.product_2 = self.env['product.product'].create(
            {'name': 'Product 2'})
        self.analytic_account = self.env['account.analytic.account'].\
            create({'name': 'test account'})
        self.tax_account = self.env['account.account'].search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_current_assets').id)],
            limit=1)

    def create_simple_invoice(self, date):
        invoice_lines = [
            (0, 0, {
                'product_id': self.product_1.id,
                'quantity': 5.0,
                'price_unit': 142.0,
                'name': 'Product that cost 142',
                'account_id': self.account_account_line.id,
                'account_analytic_id': self.analytic_account.id,
            }),
            (0, 0, {
                'product_id': self.product_2.id,
                'quantity': 4.0,
                'price_unit': 213.0,
                'name': 'Product that cost 213',
                'account_id': self.account_account_line.id,
                'account_analytic_id': self.analytic_account.id,
            })
        ]
        invoice = self.env['account.invoice'].sudo(self.manager).create({
            'partner_id': 1,
            'account_id': self.account_account.id,
            'type': 'in_invoice',
            'journal_id': self.account_journal_sale.id,
            'date_invoice': date,
            'currency_id': self.env.ref('base.EUR').id,
            'invoice_line_ids': invoice_lines,
            'state': 'draft',
        })
        invoice_tax_line = {
            'name': 'Test Tax for Customer Invoice',
            'manual': 1,
            'amount': 9050,
            'account_id': self.tax_account.id,
            'invoice_id': invoice.id,
        }
        self.env['account.invoice.tax'].sudo(self.manager).create(
            invoice_tax_line)

        return invoice

    def test_change_invoice_currency(self):
        inv = self.create_simple_invoice(fields.Date.today())
        before_curr = inv.currency_id
        before_amount = inv.amount_total
        after_curr = self.env.ref('base.USD')
        inv.write({'currency_id': after_curr.id})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, after_curr, inv.company_id, fields.Date.today())

        self.assertEqual(
            inv.amount_total, expected_value,
            'Total amount of invoice does not equal to expected value!!!')

    def test_change_validated_invoice_currency(self):
        inv = self.create_simple_invoice(fields.Date.today())
        before_amount = inv.amount_total
        inv.action_invoice_open()
        # Make sure that we can not change the currency after validated:
        inv.write({'currency_id': self.env.ref('base.USD').id})
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total, before_amount,
            'Total amount of invoice does not equal to expected value!!!')
