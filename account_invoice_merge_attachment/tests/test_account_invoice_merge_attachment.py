# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestAccountInvoiceMergeAttachment(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceMergeAttachment, self).setUp()
        self.invoice_demo = self.env.ref('account.invoice_1')
        self.attach_obj = self.env['ir.attachment']

    def test_1(self):
        invoice1 = self.invoice_demo.copy()
        invoice2 = self.invoice_demo.copy()
        self.attach_obj.create({
            'name': 'Attach1', 'datas_fname': 'Attach1',
            'datas': 'bWlncmF0aW9uIHRlc3Q=',
            'res_model': 'account.invoice', 'res_id': invoice1.id})
        invoices = invoice1 + invoice2
        invoices_info = invoices.with_context(link_attachment=True).do_merge()
        self.assertTrue(len(invoices_info.keys()) == 1)
        attach = self.attach_obj.search(
            [('res_id', 'in', invoices_info.keys()),
             ('res_model', '=', 'account.invoice')])
        self.assertTrue(len(attach) == 1)
