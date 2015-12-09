# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestAccountInvoiceParnerTimesheet(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceParnerTimesheet, self).setUp()
        self.partner_company = self.env.ref('base.res_partner_15')
        self.partner_invoice = self.env.ref('base.res_partner_address_25')
        self.partner_invoice.type = 'invoice'
        self.line_to_invoice = self.env.ref(
            'hr_timesheet.working_hours_maintenance_account_analytic_line')
        self.account_analytic = self.env.ref('account.analytic_consultancy')
        self.invoice_rate =\
            self.env.ref('hr_timesheet_invoice.timesheet_invoice_factor1')
        self.account_analytic.partner_id = self.partner_company
        self.line_to_invoice.account_id = self.account_analytic
        self.account_analytic.pricelist_id =\
            self.partner_company.property_product_pricelist and\
            self.partner_company.property_product_pricelist.id or False
        self.line_to_invoice.to_invoice = self.invoice_rate

    def test_0(self):
        # I check the partner on the analytic account
        self.assertEqual(self.line_to_invoice.account_id.partner_id.id,
                         self.partner_company.id)
        invoices = self.line_to_invoice.invoice_cost_create()
        self.assertEqual(len(invoices), 1)
        invoice_id = invoices[0]
        invoice = self.env['account.invoice'].browse([invoice_id])
        # I check if the partner on invoice is the invoice contact of partner
        # defined on analytic account
        self.assertEqual(invoice.partner_id.id, self.partner_invoice.id)
