# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
import base64
from openerp.tools import file_open
from openerp.tools import float_compare


class TestZUGFeRD(TransactionCase):

    def test_import_zugferd_invoice(self):
        zugferd_sample_files = {
            # BASIC
            'ZUGFeRD_1p0_BASIC_Einfach.pdf': {
                'invoice_number': '471102',
                'amount_untaxed': 198.0,
                'amount_total': 235.62,
                'date_invoice': '2013-03-05',
                'partner_xmlid': 'lieferant',
                },
            # Cannot handle BASIC with allowancecharge != 0 and multi-taxes
            # 'ZUGFeRD_1p0_BASIC_Rechnungskorrektur.pdf': {
            #    'type': 'in_refund',
            #    'invoice_number': 'RK21012345',
            #    'amount_untaxed': 7.67,
            #    'amount_total': 8.79,
            #    'date_invoice': '2013-09-16',
            #    'partner_xmlid': 'lieferant',
            #    },
            # COMFORT
            'ZUGFeRD_1p0_COMFORT_Einfach.pdf': {
                'invoice_number': '471102',
                'amount_untaxed': 473.0,
                'amount_total': 529.87,
                'date_invoice': '2013-03-05',
                'date_due': '2013-04-04',
                'partner_xmlid': 'lieferant',
                },
            'ZUGFeRD_1p0_COMFORT_Einfach.pdf-ZUGFeRD-invoice.xml': {
                'invoice_number': '471102',
                'amount_untaxed': 473.0,
                'amount_total': 529.87,
                'date_invoice': '2013-03-05',
                'partner_xmlid': 'lieferant',
                },
            'ZUGFeRD_1p0_COMFORT_Haftpflichtversicherung_'
            'Versicherungssteuer.pdf': {
                'invoice_number': '01.234.567.8-2014-1',
                'amount_untaxed': 50.00,
                'amount_total': 59.50,
                'date_invoice': '2014-01-24',
                # stupid sample files: due date is before invoice date !
                'date_due': '2013-12-06',
                'partner_xmlid': 'mvm_musterhafter',
                },
            'ZUGFeRD_1p0_COMFORT_Kraftfahrversicherung_'
            'Bruttopreise.pdf': {
                'invoice_number': '00.123.456.7-2014-1',
                'amount_untaxed': 184.88,
                # XML says 184.87 because they seem to use rounded sum
                # instead of the sum of rounded
                'amount_total': 220.0,
                'date_invoice': '2014-03-11',
                'date_due': '2014-04-01',
                'partner_xmlid': 'mvm_musterhafter',
                },
            # Disabled due to a bug in the XML
            # Contains Charge + allowance
            # 'ZUGFeRD_1p0_COMFORT_Rabatte.pdf': {
            #    'invoice_number': '471102',
            #    'amount_untaxed': 193.77,
            # There is a bug in the total amount of the last line
            # (55.46 ; right value is 20 x 2.7700 = 55.40)
            #    'amount_total': 215.14,
            #    'date_invoice': '2013-06-05',
            #    'partner_xmlid': 'lieferant',
            #    },
            # has AllowanceTotalAmount
            'ZUGFeRD_1p0_COMFORT_Rechnungskorrektur.pdf': {
                'type': 'in_refund',
                'invoice_number': 'RK21012345',
                'date_invoice': '2013-09-16',
                'amount_untaxed': 7.67,
                'amount_total': 8.79,
                'partner_xmlid': 'lieferant',
                },
            'ZUGFeRD_1p0_COMFORT_Sachversicherung_berechneter_'
            'Steuersatz.pdf': {
                'invoice_number': '00.123.456.7-2014-1',
                'amount_untaxed': 1000.00,
                'amount_total': 1163.40,
                'date_invoice': '2014-04-18',
                'date_due': '2014-05-21',
                'partner_xmlid': 'mvm_musterhafter',
                },
            'ZUGFeRD_1p0_COMFORT_SEPA_Prenotification.pdf': {
                'invoice_number': '471102',
                'amount_untaxed': 473.00,
                'amount_total': 529.87,
                'date_invoice': '2014-03-05',
                'date_due': '2014-03-20',
                'partner_xmlid': 'lieferant',
                },
            # EXTENDED
            # has AllowanceTotalAmount
            'ZUGFeRD_1p0_EXTENDED_Kostenrechnung.pdf': {
                'invoice_number': 'KR87654321012',
                'amount_untaxed': 1056.05,
                'amount_total': 1256.70,
                'date_invoice': '2013-10-06',
                'partner_xmlid': 'musterlieferant',
                },
            'ZUGFeRD_1p0_EXTENDED_Rechnungskorrektur.pdf': {
                'type': 'in_refund',
                'invoice_number': 'RK21012345',
                'amount_untaxed': 7.67,
                'amount_total': 8.79,
                'date_invoice': '2013-09-16',
                'partner_xmlid': 'musterlieferant',
                },
            'ZUGFeRD_1p0_EXTENDED_Warenrechnung.pdf': {
                'invoice_number': 'R87654321012345',
                'amount_untaxed': 448.99,
                'amount_total': 518.99,
                'date_invoice': '2013-08-06',
                'partner_xmlid': 'musterlieferant',
                },
            }
        aio = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Account')
        # We need precision of product price at 4
        # in order to import ZUGFeRD_1p0_EXTENDED_Kostenrechnung.pdf
        price_precision = self.env.ref('product.decimal_price')
        price_precision.digits = 4
        for (zugferd_file, res_dict) in zugferd_sample_files.iteritems():
            f = file_open(
                'account_invoice_import_zugferd/tests/files/' +
                zugferd_file, 'rb')
            pdf_file = f.read()
            f.close()
            wiz = self.env['account.invoice.import'].create({
                'invoice_file': base64.b64encode(pdf_file),
                'invoice_filename': zugferd_file,
                })
            wiz.import_invoice()
            invoices = aio.search([
                ('state', '=', 'draft'),
                ('type', 'in', ('in_invoice', 'in_refund')),
                ('supplier_invoice_number', '=', res_dict['invoice_number'])
                ])
            self.assertEqual(len(invoices), 1)
            inv = invoices[0]
            self.assertEqual(inv.type, res_dict.get('type', 'in_invoice'))
            self.assertEqual(inv.date_invoice, res_dict['date_invoice'])
            if res_dict.get('date_due'):
                self.assertEqual(inv.date_due, res_dict['date_due'])
            self.assertEqual(inv.partner_id, self.env.ref(
                'account_invoice_import_zugferd.' +
                res_dict['partner_xmlid']))
            self.assertFalse(float_compare(
                inv.amount_untaxed, res_dict['amount_untaxed'],
                precision_digits=precision))
            self.assertFalse(float_compare(
                inv.check_total, res_dict['amount_total'],
                precision_digits=precision))
            self.assertFalse(float_compare(
                inv.amount_total, res_dict['amount_total'],
                precision_digits=precision))
            # Delete because several sample invoices have the same number
            invoices.unlink()
