# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
import logging

logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_pdf(
            self, cr, uid, ids, report_name, html=None, data=None,
            context=None):
        """We go through that method when the PDF is generated for the 1st
        time and also when it is read from the attachment.
        This method is specific to QWeb"""
        pdf_content = super(Report, self).get_pdf(
            cr, uid, ids, report_name, html=html, data=data, context=context)
        if report_name == 'account.report_invoice' and len(ids) == 1:
            invoice = self.pool['account.invoice'].browse(
                cr, uid, ids[0], context=context)
            pdf_content = invoice.regular_pdf_invoice_to_zugferd_invoice(
                pdf_content)
        return pdf_content

# TODO : the PDF saved as attachment is NOT the good one...
# but the PDF opened from the attachment is OK !
# because we don't inherit the right method.
# get_pdf() calls _run_wkhtmltopdf() which generate
# AND SAVE AS ATTACHMENT the report. So we need a hook inside _run_wkhtmltopdf
# but there is no hook for the moment
# The problem is the same in the module
# OCA/reporting-engines/report_qweb_signer
