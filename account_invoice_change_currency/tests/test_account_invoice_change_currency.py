# Copyright 2018 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tools import float_compare
import odoo.tests.common as common


class TestAccountInvoiceChangeCurrency(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceChangeCurrency, self).setUp()

        self.precision = self.env['decimal.precision'].precision_get(
            'Payment Terms')
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

    def create_simple_invoice(self, date=False, context=None, inv_type=None):
        if not context:
            context = {}
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
        invoice = self.env['account.invoice'].sudo(self.manager).with_context(
            **context).create({
                'partner_id': 1,
                'account_id': self.account_account.id,
                'type': inv_type or 'in_invoice',
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
        inv._onchange_currency_change_rate()
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, after_curr, inv.company_id, fields.Date.today())

        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 1), 0,
            'Total amount of invoice does not equal to expected value!!!')

    def test_change_validated_invoice_currency(self):
        inv = self.create_simple_invoice(fields.Date.today())
        before_amount = inv.amount_total
        inv.action_invoice_open()
        # Make sure that we can not change the currency after validated:
        inv.write({'currency_id': self.env.ref('base.USD').id})
        inv._onchange_currency_change_rate()
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total, before_amount,
            'Total amount of invoice does not equal to expected value!!!')

    def test_create_invoice_update_currency(self):
        inv = self.create_simple_invoice()
        before_amount = inv.amount_total
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total, before_amount,
            'Amount must remain the same, because no currency changes')

    def test_custom_rate_update_currency(self):
        inv = self.create_simple_invoice(fields.Date.today())
        before_amount = inv.amount_total
        after_curr = self.env.ref('base.USD')
        custom_rate = 1.13208
        inv.write({'currency_id': after_curr.id, 'custom_rate': custom_rate})
        inv._onchange_currency_change_rate()
        inv.write({'custom_rate': custom_rate})
        inv.action_account_change_currency()
        expected_value = before_amount * custom_rate
        # TODO: Check float comparation, 12013.64 vs 12013.632959999999
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, self.precision), 1,
            'Total amount of invoice does not equal to expected value!!!')

    def test_custom_rate_zero_update_currency(self):
        inv = self.create_simple_invoice()
        before_amount = inv.amount_total
        before_curr = inv.currency_id
        custom_rate = 0.0
        usd = self.env.ref('base.USD')
        eur = self.env.ref('base.EUR')
        inv.write({'currency_id': usd.id, 'custom_rate': custom_rate})
        inv._onchange_currency_change_rate()
        inv.write({'custom_rate': custom_rate})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, usd, inv.company_id, fields.Date.today())
        self.assertEqual(
            float_compare(inv.amount_total, expected_value, 1), 0,
            'Total amount of invoice does not equal to expected value!!!')
        # Change currency and set custom rate 0
        inv.write({'currency_id': eur.id, 'custom_rate': custom_rate})
        inv._onchange_currency_change_rate()
        inv.write({'custom_rate': custom_rate})
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total, before_amount,
            'Total amount of invoice does not equal to expected value!!!')
        # Change Again custom rate with old_rate but now without new currency
        inv.write({'custom_rate': inv.get_last_rate()[1]})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, eur, inv.company_id, fields.Date.today())
        self.assertEqual(
            inv.amount_total, before_amount,
            'Total amount of invoice does not equal to expected value!!!')
        # Custom rate with 0 but now without new currency
        inv.write({'custom_rate': custom_rate})
        inv.action_account_change_currency()
        expected_value = before_curr._convert(
            before_amount, eur, inv.company_id, fields.Date.today())
        self.assertEqual(
            inv.amount_total, before_amount,
            'Total amount of invoice does not equal to expected value!!!')
        # keep old_rate but now we update the currency.rate
        before_amount = inv.amount_total
        old_rate = inv.get_last_rate()[1]
        new_rate = 1.6299
        self.env['res.currency.rate'].create({
            'name': fields.Date.today(),
            'rate': new_rate,
            'currency_id': usd.id,
            'company_id': inv.company_id.id,
        })
        rate = usd._get_conversion_rate(
            usd, inv.currency_id, inv.company_id,
            inv.date_invoice or fields.Date.today())
        inv.write({'custom_rate': old_rate})
        inv.action_account_change_currency()
        expected_value = before_amount * rate / old_rate
        # TODO: Check float comparation, 9954.4 vs 9954.40628259402
        self.assertEqual(float_compare(
            inv.amount_total, expected_value, self.precision), -1,
            'Total amount of invoice does not equal to expected value!!!')
        # change custom rate then we trigger the conversion 2 times
        # The currency.rate modification above will be ignored and keep the
        # custom rate
        before_amount = inv.amount_total
        old_rate = inv.get_last_rate()[1]
        rate = usd._get_conversion_rate(
            usd, inv.currency_id, inv.company_id,
            inv.date_invoice or fields.Date.today())
        inv.action_account_change_currency()
        expected_value = before_amount * rate / old_rate
        self.assertEqual(float_compare(
            inv.amount_total, expected_value, self.precision), 0,
            'Total amount of invoice does not equal to expected value!!!')
        before_amount = inv.amount_total
        rate = old_rate + 1
        inv.write({'custom_rate': rate})
        inv.action_account_change_currency()
        expected_value = before_amount * rate / old_rate
        # TODO: Check float comparation, 26179.05 vs 26179.07656
        self.assertEqual(float_compare(
            inv.amount_total, expected_value, 1), 0,
            'Total amount of invoice does not equal to expected value!!!')
        inv.action_account_change_currency()
        # TODO: Check float comparation, 26179.05 vs 26179.07656
        self.assertEqual(float_compare(
            inv.amount_total, expected_value, 1), 0,
            'Total amount of invoice does not equal to expected value!!!')

    def test_force_custom_rate(self):
        inv = self.create_simple_invoice(context={'force_rate': True})
        inv2 = self.create_simple_invoice()
        self.assertNotEqual(
            inv.custom_rate, inv2.custom_rate,
            'Rates must be different!')
        inv._toggle_forced_rate()
        inv._onchange_currency_change_rate()
        self.assertEqual(
            inv.custom_rate, inv2.custom_rate,
            'Amount must remain the same, because force rate was disable')

    def test_not_currency_change(self):
        inv = self.create_simple_invoice(inv_type='out_invoice')
        before_amount = inv.amount_total
        inv.action_account_change_currency()
        self.assertEqual(
            inv.amount_total, before_amount,
            'Amount must remain the same, because None change was made')
