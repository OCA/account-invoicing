# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
import PyPDF2
from lxml import etree
from StringIO import StringIO


class TestZUGFeRDInvoice(TransactionCase):

    def test_print_demo_customer_invoice(self):
        aio = self.env['account.invoice']
        for i in range(5):
            invoice = self.env.ref('account.invoice_%d' % (i+1))
            pdf_content = self.registry['report'].get_pdf(
                self.cr, self.uid, [invoice.id], 'account.report_invoice')
            self.assertTrue(aio.pdf_is_zugferd(pdf_content))

    def test_deep_customer_invoice(self):
        invoice = self.env.ref('account.invoice_3')
        pdf_content = self.registry['report'].get_pdf(
            self.cr, self.uid, [invoice.id], 'account.report_invoice')
        fd = StringIO(pdf_content)
        pdf = PyPDF2.PdfFileReader(fd)
        pdf_root = pdf.trailer['/Root']
        embeddedfile = pdf_root['/Names']['/EmbeddedFiles']['/Names']
        self.assertEquals(embeddedfile[0], 'ZUGFeRD-invoice.xml')
        zugferd_file_dict_obj = embeddedfile[1]
        zugferd_file_dict = zugferd_file_dict_obj.getObject()
        xml_string = zugferd_file_dict['/EF']['/F'].getData()
        xml_root = etree.fromstring(xml_string)
        self.assertTrue(xml_root.tag.startswith(
            '{urn:ferd:CrossIndustryDocument:invoice:1p0'))
