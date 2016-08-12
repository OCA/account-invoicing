# -*- coding: utf-8 -*-
# © 2015-2016 Akretion France (www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# The licence is in the file __openerp__.py

from openerp.tests.common import TransactionCase
import base64
from openerp.tools import file_open, float_compare


class TestInvoiceImport(TransactionCase):

    def setUp(self):
        super(TestInvoiceImport, self).setUp()
        frtax = self.env['account.tax'].create({
            'name': 'French VAT purchase 20.0%',
            'description': 'FR-VAT-buy-20.0',
            'amount': 0.2,
            'type': 'percent',
            'account_collected_id': self.env.ref('account.a_expense').id,
            'account_paid_id': self.env.ref('account.a_expense').id,
            'base_sign': -1,
            'tax_sign': -1,
            'type_tax_use': 'purchase',
            })
        # Set this tax on Internet access product
        internet_product = self.env.ref(
            'account_invoice_import_invoice2data.internet_access')
        internet_product.supplier_taxes_id = [(6, 0, [frtax.id])]

    def test_import_free_invoice(self):
        f = file_open(
            'account_invoice_import_invoice2data/tests/pdf/'
            'invoice_free_fiber_201507.pdf',
            'rb')
        pdf_file = f.read()
        wiz = self.env['account.invoice.import'].create({
            'invoice_file': base64.b64encode(pdf_file),
            'invoice_filename': 'invoice_free_fiber_201507.pdf',
        })
        f.close()
        wiz.import_invoice()
        # Check result of invoice creation
        invoices = self.env['account.invoice'].search([
            ('state', '=', 'draft'),
            ('type', '=', 'in_invoice'),
            ('supplier_invoice_number', '=', '562044387')
            ])
        self.assertEquals(len(invoices), 1)
        inv = invoices[0]
        self.assertEquals(inv.type, 'in_invoice')
        self.assertEquals(inv.date_invoice, '2015-07-02')
        self.assertEquals(
            inv.partner_id,
            self.env.ref('account_invoice_import_invoice2data.free'))
        self.assertEquals(inv.journal_id.type, 'purchase')
        self.assertEquals(
            float_compare(inv.check_total, 29.99, precision_digits=2), 0)
        self.assertEquals(
            float_compare(inv.amount_total, 29.99, precision_digits=2), 0)
        self.assertEquals(
            float_compare(inv.amount_untaxed, 24.99, precision_digits=2), 0)
        self.assertEquals(
            len(inv.invoice_line), 1)
        iline = inv.invoice_line[0]
        self.assertEquals(iline.name, 'Fiber optic access at the main office')
        self.assertEquals(
            iline.product_id,
            self.env.ref(
                'account_invoice_import_invoice2data.internet_access'))
        self.assertEquals(
            float_compare(iline.quantity, 1.0, precision_digits=0), 0)
        self.assertEquals(
            float_compare(iline.price_unit, 24.99, precision_digits=2), 0)

        # Prepare data for next test i.e. invoice update
        # (we re-use the invoice created by the first import !)
        inv.write({
            'date_invoice': False,
            'supplier_invoice_number': False,
            'check_total': False,
            })

        # New import with update of an existing draft invoice
        f = file_open(
            'account_invoice_import_invoice2data/tests/pdf/'
            'invoice_free_fiber_201507.pdf',
            'rb')
        pdf_file = f.read()
        wiz2 = self.env['account.invoice.import'].create({
            'invoice_file': base64.b64encode(pdf_file),
            'invoice_filename': 'invoice_free_fiber_201507.pdf',
            })
        f.close()
        action = wiz2.import_invoice()
        # Choose to update the existing invoice
        wiz2.with_context(action['context']).update_invoice()
        invoices = self.env['account.invoice'].search([
            ('state', '=', 'draft'),
            ('type', '=', 'in_invoice'),
            ('supplier_invoice_number', '=', '562044387')
            ])
        self.assertEquals(len(invoices), 1)
        inv = invoices[0]
        self.assertEquals(inv.date_invoice, '2015-07-02')
        self.assertEquals(
            float_compare(inv.check_total, 29.99, precision_digits=2), 0)
