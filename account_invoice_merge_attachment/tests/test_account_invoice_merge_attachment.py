# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceMergeAttachment(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceMergeAttachment, self).setUp()
        self.AttachmentObj = self.env['ir.attachment']
        self.InvoiceObj = self.env['account.invoice']

        self.partner = self.env.ref('base.main_partner')
        self.product = self.env.ref('product.product_product_8')
        self.product_account = self.product.property_account_income_id or \
            self.product.categ_id.property_account_income_categ_id

    def create_invoice(self):
        return self.InvoiceObj.create({
            'partner_id': self.partner.id,
            'name': "Test",
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'account_id': self.product_account.id,
                    'quantity': 1,
                    'price_unit': 1,
                })
            ]
        })

    def create_invoice_attachment(self, invoice):
        return self.AttachmentObj.create({
            'name': 'Attach',
            'datas_fname': 'Attach',
            'datas': 'bWlncmF0aW9uIHRlc3Q=',
            'res_model': 'account.invoice',
            'res_id': invoice.id
        })

    def test_merge_invoice_attachments(self):
        invoice1 = self.create_invoice()
        self.create_invoice_attachment(invoice1)

        invoice2 = self.create_invoice()
        self.create_invoice_attachment(invoice2)
        self.create_invoice_attachment(invoice2)

        invoices = invoice1 + invoice2
        invoices_info = invoices.with_context(link_attachment=True).do_merge()
        self.assertTrue(len(invoices_info.keys()) == 1)
        attach = self.AttachmentObj.search([
            ('res_id', 'in', invoices_info.keys()),
            ('res_model', '=', 'account.invoice')
        ])
        self.assertEquals(
            len(attach), 3,
            msg="Merged invoiced should have 3 attachments")
