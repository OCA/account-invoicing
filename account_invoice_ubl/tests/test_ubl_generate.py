# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp import workflow


class TestUblInvoice(TransactionCase):

    def test_ubl_generate(self):
        ro = self.registry['report']
        buo = self.env['base.ubl']
        for i in range(5):
            i += 1
            invoice = self.env.ref('account.invoice_%d' % i)
            invoice_filename = invoice.get_ubl_filename()
            # validate invoice
            workflow.trg_validate(
                self.uid, 'account.invoice', invoice.id, 'invoice_open',
                self.cr)
            if invoice.type not in ('out_invoice', 'out_refund'):
                continue
            # I didn't manage to make it work with new api :-(
            pdf_file = ro.get_pdf(
                self.cr, self.uid, invoice.ids,
                'account.report_invoice')
            res = buo.get_xml_files_from_pdf(pdf_file)
            self.assertTrue(invoice_filename in res)
