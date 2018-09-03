# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestCorrispettiviSale(AccountingTestCase):

    def setUp(self):
        super(TestCorrispettiviSale, self).setUp()
        fiscal_position_model = self.env['account.fiscal.position']
        partner_model = self.env['res.partner']
        self.invoice_model = self.env['account.invoice']
        self.sale_model = self.env['sale.order']
        self.corr_fiscal_position = fiscal_position_model.create({
            'name': 'corrispettivi fiscal position',
            'corrispettivi': True
        })
        self.no_corr_fiscal_position = fiscal_position_model.create({
            'name': 'corrispettivi fiscal position',
            'corrispettivi': False
        })
        self.corrispettivi_partner = partner_model.create({
            'name': 'Corrispettivi partner',
            'use_corrispettivi': True,
            'property_account_position_id': self.corr_fiscal_position.id
        })
        self.no_corrispettivi_partner = partner_model.create({
            'name': 'Corrispettivi partner',
            'use_corrispettivi': False,
            'property_account_position_id': self.no_corr_fiscal_position.id
        })

        self.account_receivable = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)
        self.product = self.env['product.product'].search([], limit=1)

    def create_corr_journal(self):
        corr_journal_id = self.env['account.journal'].create({
            'name': 'CORR',
            'code': 'CORR',
            'type': 'sale',
            'corrispettivi': True
        })
        return corr_journal_id

    def create_no_corr_journal(self):
        no_corr_journal_id = self.env['account.journal'].create({
            'name': 'NOCORR',
            'code': 'NOCORR',
            'type': 'sale',
            'corrispettivi': False
        })
        return no_corr_journal_id

    def create_corrispettivi_sale(self):
        corr_sale = self.sale_model \
            .create({
                'partner_id': self.corrispettivi_partner.id,
                'order_line': [(0, 0, {
                    'product_id': self.product.id
                })]})
        corr_sale.onchange_partner_corrispettivi_sale()
        return corr_sale

    def create_no_corrispettivi_sale(self):
        no_corr_sale = self.sale_model \
            .create({
                'partner_id': self.no_corrispettivi_partner.id,
                'order_line': [(0, 0, {
                    'product_id': self.product.id
                })]})
        no_corr_sale.onchange_partner_corrispettivi_sale()
        return no_corr_sale

    def test_corrispettivi_sale_onchange(self):
        """ Test onchange in sale order. """
        sale = self.create_corrispettivi_sale()
        self.assertTrue(sale.corrispettivi)

        sale.partner_id = self.no_corrispettivi_partner
        sale.onchange_partner_corrispettivi_sale()
        self.assertFalse(sale.corrispettivi)

    def test_corrispettivi_sale_invoice(self):
        """
        Test corrispettivo creation for a sale order having flag corrispettivi.
        """
        self.create_corr_journal()
        sale = self.create_corrispettivi_sale()
        self.assertTrue(sale.action_confirm())
        invoice_ids_list = sale.action_invoice_create()
        self.assertTrue(len(invoice_ids_list))
        for invoice_id in invoice_ids_list:
            invoice = self.invoice_model.browse(invoice_id)
            self.assertTrue(invoice.corrispettivo)

    def test_no_corrispettivi_sale_invoice(self):
        """
        Test invoice creation for a sale order not having flag corrispettivi.
        """
        self.create_corr_journal()
        sale = self.create_no_corrispettivi_sale()
        self.assertTrue(sale.action_confirm())
        invoice_ids_list = sale.action_invoice_create()
        for invoice_id in invoice_ids_list:
            invoice = self.invoice_model.browse(invoice_id)
            self.assertFalse(invoice.corrispettivo)

    def test_no_corrispettivi_sale_invoice_journal(self):
        """
        Test invoice creation for a sale order not having flag corrispettivi,
        in the case that the selected journal is corrispettivi.
        """
        for journal in self.env['account.journal'].search([]):
            journal.active = False
        self.create_corr_journal()
        self.create_no_corr_journal()
        sale = self.create_no_corrispettivi_sale()
        self.assertTrue(sale.action_confirm())
        invoice_ids_list = sale.action_invoice_create()
        for invoice_id in invoice_ids_list:
            invoice = self.invoice_model.browse(invoice_id)
            self.assertFalse(invoice.corrispettivo)
