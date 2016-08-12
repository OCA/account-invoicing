# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, tools, _
from openerp.exceptions import Warning as UserError
from datetime import datetime
import os
from tempfile import mkstemp
import logging
from invoice2data.main import extract_data
from invoice2data.template import read_templates

logger = logging.getLogger(__name__)


class AccountInvoiceImport(models.TransientModel):
    _inherit = 'account.invoice.import'

    @api.model
    def fallback_parse_pdf_invoice(self, file_data):
        '''This method must be inherited by additionnal modules with
        the same kind of logic as the account_bank_statement_import_*
        modules'''
        logger.info('Trying to analyze PDF invoice with invoice2data lib')
        fd, file_name = mkstemp()
        try:
            os.write(fd, file_data)
        finally:
            os.close(fd)
        local_templates_dir = tools.config.get(
            'invoice2data_templates_dir', False)
        logger.debug(
            'invoice2data local_templates_dir=%s', local_templates_dir)
        templates = None
        if local_templates_dir and os.path.isdir(local_templates_dir):
            templates = read_templates(local_templates_dir)
        logger.debug(
            'Calling invoice2data.extract_data with templates=%s',
            templates)
        try:
            res = extract_data(file_name, templates=templates)
        except Exception, e:
            raise UserError(_(
                "PDF Invoice parsing failed. Error message: %s") % e)
        if not res:
            raise UserError(_(
                "This PDF invoice doesn't match a known template of "
                "the invoice2data lib."))
        logger.info('Result of invoice2data PDF extraction: %s', res)
        # rewrite a few keys
        res['amount_total'] = res.pop('amount')
        # If you crash here, you should just update invoice2data to the
        # latest version from github
        res['currency_iso'] = res.pop('currency')
        if 'vat' in res:
            res['partner_vat'] = res.pop('vat')
        return res
