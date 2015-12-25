# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Invoice PDF import module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare, float_round
from openerp.exceptions import Warning as UserError
from datetime import datetime
import logging
import os
import base64
from tempfile import mkstemp
from invoice2data.main import extract_data
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from lxml import etree
import StringIO

logger = logging.getLogger(__name__)


class AccountInvoicePdfImport(models.TransientModel):
    _name = 'account.invoice.pdf.import'
    _description = 'Wizard to import supplier invoices/refunds as PDF'

    pdf_file = fields.Binary(
        string='PDF Invoice', required=True)
    pdf_filename = fields.Char(string='Filename')
    state = fields.Selection([
        ('import', 'Import'),
        ('update', 'Update'),
        ], string='State', default="import")
    partner_id = fields.Many2one(
        'res.partner', string="Supplier", readonly=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', readonly=True)
    amount_untaxed = fields.Float(
        string='Total Untaxed', digits=dp.get_precision('Account'),
        readonly=True)
    amount_total = fields.Float(
        string='Total', digits=dp.get_precision('Account'),
        readonly=True)
    invoice_id = fields.Many2one(
        'account.invoice', string='Draft Supplier Invoice to Update')

    @api.model
    def parse_invoice_with_embedded_xml(self, file_data):
        logger.info('Trying to find an embedded XML file inside PDF')
        fd = StringIO.StringIO(file_data)
        parser = PDFParser(fd)
        doc = PDFDocument(parser)
        logger.debug('doc.catalog=%s', doc.catalog)
        # The code below will have to be adapted when we get samples
        # of PDF files with embedded XML other than ZUGFeRD
        embeddedfile = doc.catalog['Names']['EmbeddedFiles']['Names']
        if embeddedfile[0] == 'ZUGFeRD-invoice.xml':
            pdfobjref1 = embeddedfile[1]
        else:
            logger.info('No embedded file ZUGFeRD-invoice.xml')
            return False
        logger.debug('pdfobjref1=%s', pdfobjref1)
        respdfobjref1 = resolve1(pdfobjref1)
        pdfobjref2 = respdfobjref1['EF']['F']
        respdfobjref2 = resolve1(pdfobjref2)
        xml_string = respdfobjref2.get_data()
        xml_root = etree.fromstring(xml_string)
        logger.info('A valid XML file has been found in the PDF file')
        logger.debug('xml_root:')
        logger.debug(etree.tostring(
            xml_root, pretty_print=True, encoding='UTF-8',
            xml_declaration=True))
        return self.parse_cii_xml(xml_root)

    @api.model
    def parse_cii_xml(self, xml_root):
        """Parse Core Industry Invoice XML file"""
        assert xml_root.tag.startswith(
            '{urn:ferd:CrossIndustryDocument:invoice:1p0'),\
            'wrong Core Industry Invoice namespace'
        namespaces = xml_root.nsmap
        logger.debug('XML file namespaces=%s', namespaces)
        inv_number_xpath = xml_root.xpath(
            '//rsm:HeaderExchangedDocument/ram:ID', namespaces=namespaces)
        supplier_xpath = xml_root.xpath(
            '//ram:ApplicableSupplyChainTradeAgreement'
            '/ram:SellerTradeParty'
            '/ram:Name', namespaces=namespaces)
        vat_xpath = xml_root.xpath(
            '//ram:ApplicableSupplyChainTradeAgreement'
            "/ram:SellerTradeParty"
            "/ram:SpecifiedTaxRegistration"
            "/ram:ID[@schemeID='VA']",
            namespaces=namespaces)
        date_xpath = xml_root.xpath(
            '//rsm:HeaderExchangedDocument'
            '/ram:IssueDateTime/udt:DateTimeString', namespaces=namespaces)
        date_dt = datetime.strptime(date_xpath[0].text, '%Y%m%d')
        currency_iso_xpath = xml_root.xpath(
            "//ram:ApplicableSupplyChainTradeSettlement"
            "/ram:InvoiceCurrencyCode",
            namespaces=namespaces)
        amount_total_xpath = xml_root.xpath(
            "//ram:ApplicableSupplyChainTradeSettlement"
            "/ram:SpecifiedTradeSettlementMonetarySummation/"
            "ram:GrandTotalAmount",
            namespaces=namespaces)
        amount_untaxed_xpath = xml_root.xpath(
            "//ram:ApplicableSupplyChainTradeSettlement"
            "/ram:SpecifiedTradeSettlementMonetarySummation"
            "/ram:TaxBasisTotalAmount", namespaces=namespaces)
        iban_xpath = xml_root.xpath(
            "//ram:SpecifiedTradeSettlementPaymentMeans"
            "/ram:PayeePartyCreditorFinancialAccount"
            "/ram:IBANID", namespaces=namespaces)
        bic_xpath = xml_root.xpath(
            "//ram:SpecifiedTradeSettlementPaymentMeans"
            "/ram:PayeeSpecifiedCreditorFinancialInstitution"
            "/ram:BICID", namespaces=namespaces)
        inv_line_xpath = xml_root.xpath(
            "//ram:IncludedSupplyChainTradeLineItem", namespaces=namespaces)
        res_lines = []
        for iline in inv_line_xpath:
            price_unit_xpath = iline.xpath(
                "ram:SpecifiedSupplyChainTradeAgreement"
                "/ram:NetPriceProductTradePrice"
                "/ram:ChargeAmount",
                namespaces=namespaces)
            qty_xpath = iline.xpath(
                "ram:SpecifiedSupplyChainTradeDelivery/ram:BilledQuantity",
                namespaces=namespaces)
            if not qty_xpath:
                continue
            qty = float(qty_xpath[0].text)
            ean13_xpath = iline.xpath(
                "ram:SpecifiedTradeProduct/ram:GlobalID",
                namespaces=namespaces)
            # Check SchemeID ?
            product_code_xpath = iline.xpath(
                "ram:SpecifiedTradeProduct/ram:SellerAssignedID",
                namespaces=namespaces)
            name_xpath = iline.xpath(
                "ram:SpecifiedTradeProduct/ram:Name",
                namespaces=namespaces)
            if price_unit_xpath:
                price_unit = float(price_unit_xpath[0].text)
            else:
                price_subtotal_xpath = iline.xpath(
                    "ram:SpecifiedSupplyChainTradeSettlement"
                    "/ram:SpecifiedTradeSettlementMonetarySummation"
                    "/ram:LineTotalAmount",
                    namespaces=namespaces)
                price_subtotal = float(price_subtotal_xpath[0].text)
                price_unit = price_subtotal / qty
            vals = {
                'ean13': ean13_xpath and ean13_xpath[0].text or False,
                'product_code':
                product_code_xpath and product_code_xpath[0].text or False,
                'quantity': qty,
                'price_unit': price_unit,
                'name': name_xpath[0].text,
                }
            res_lines.append(vals)
        res = {
            'vat': vat_xpath[0].text,
            'partner_name': supplier_xpath[0].text,
            'invoice_number': inv_number_xpath[0].text,
            'date': fields.Date.to_string(date_dt),
            'currency_iso': currency_iso_xpath[0].text,
            'amount_total': float(amount_total_xpath[0].text),
            'amount_untaxed': float(amount_untaxed_xpath[0].text),
            'iban': iban_xpath and iban_xpath[0].text or False,
            'bic': bic_xpath and bic_xpath[0].text or False,
            'lines': res_lines,
            }
        # Hack for the sample ZUGFeRD invoices that use an invalid VAT number !
        if res['vat'] == 'DE123456789':
            res.pop('vat')
        logger.info('Result of CII XML parsing: %s', res)
        return res

    @api.model
    def parse_invoice_with_invoice2data(self, file_data):
        logger.info('Trying to analyze PDF invoice with invoice2data lib')
        fd, file_name = mkstemp()
        try:
            os.write(fd, file_data)
        finally:
            os.close(fd)
        try:
            res = extract_data(file_name)
        except:
            raise UserError(_(
                "PDF Invoice parsing failed."))
        if not res:
            raise UserError(_(
                "This PDF invoice doesn't match a known template of "
                "the invoice2data lib."))
        # rewrite a few keys
        res['amount_total'] = res['amount']
        res.pop('amount')
        # convert datetime to string, to make it json serializable
        for key, value in res.iteritems():
            if value and isinstance(value, datetime):
                res[key] = fields.Date.to_string(value)
        logger.info('Result of invoice2data PDF extraction: %s', res)
        return res
        # Dict to return:
        # {
        # 'currency_iso': 'EUR',
        # 'currency_symbol': u'€',  # The one or the other
        # 'date': '2015-10-08',  # Must be a string
        # 'date_due': '2015-11-07',
        # 'amount_untaxed': 10.0,
        # 'amount_total': 12.0,  # Total with taxes
        # 'vat': 'FR25499247138',
        # 'partner_name': 'Capitaine Train'  # Not needed if we have VAT
        # 'invoice_number': 'I1501243',
        # 'description': 'TGV Paris-Lyon',
        # 'lines': [{
        #       'ean13': '4123456000021',
        #       'price_unit': 1.45,  # price_unit always positive
        #       'product_code': 'GZ250',
        #       'name': 'Gelierzucker Extra 250g',
        #       'quantity': -2.0,  # < 0 when it's a refund
        #       }],
        # }

    @api.model
    def _select_partner(self, parsed_inv):
        if parsed_inv.get('vat'):
            vat = parsed_inv['vat'].replace(' ', '')
            # Match even if the VAT number has spaces in Odoo
            self._cr.execute(
                """SELECT id FROM res_partner
                WHERE supplier=true
                AND is_company=true
                AND replace(vat, ' ', '') = %s""",
                (vat, ))
            res = self._cr.fetchall()
            if res:
                partner_id = res[0][0]
                return self.env['res.partner'].browse(partner_id)
            else:
                raise UserError(_(
                    "The analysis of the PDF invoice returned '%s' as "
                    "supplier VAT number. But there are no supplier "
                    "with this VAT number in Odoo.") % vat)
        elif parsed_inv.get('partner_name'):
            partners = self.env['res.partner'].search([
                ('name', '=ilike', parsed_inv['partner_name']),
                ('is_company', '=', True),
                ('supplier', '=', True)])
            if partners:
                return partners[0]
            else:
                raise UserError(_(
                    "PDF Invoice parsing didn't return the VAT number of the "
                    "supplier and the returned supplier name (%s) "
                    "is not a supplier company in Odoo.")
                    % parsed_inv['partner_name'])

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv):
        aio = self.env['account.invoice']
        ailo = self.env['account.invoice.line']
        company = self.env.user.company_id
        assert parsed_inv.get('amount_total'), 'Missing amount_total'
        vals = {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'type': parsed_inv['type'],
            'company_id': company.id,
            'supplier_invoice_number':
            parsed_inv.get('invoice_number'),
            'date_invoice': parsed_inv.get('date'),
            'journal_id':
            aio.with_context(type='in_invoice')._default_journal().id,
            'invoice_line': [],
            'check_total': parsed_inv.get('amount_total'),
            }
        vals.update(aio.onchange_partner_id(
            'in_invoice', self.partner_id.id, company_id=company.id)['value'])
        # Force due date of the invoice
        if parsed_inv.get('date_due'):
            vals['date_due'] = parsed_inv.get('date_due')
        # Bank info
        if parsed_inv.get('iban'):
            iban = parsed_inv.get('iban').replace(' ', '')
            self._cr.execute(
                """SELECT id FROM res_partner_bank
                WHERE replace(acc_number, ' ', '')=%s
                AND state='iban'
                AND partner_id=%s
                """, (iban, vals['partner_id']))
            rpb_res = self._cr.fetchall()
            if rpb_res:
                vals['partner_bank_id'] = rpb_res[0][0]
            else:
                partner_bank = self.env['res.partner.bank'].create({
                    'partner_id': vals['partner_id'],
                    'state': 'iban',
                    'acc_number': parsed_inv['iban'],
                    'bank_bic': parsed_inv.get('bic'),
                    })
                vals['partner_bank_id'] = partner_bank.id
                parsed_inv['chatter_msg'] = _(
                    "The bank account <b>IBAN %s</b> has been automatically "
                    "added on the supplier <b>%s</b>") % (
                        parsed_inv['iban'], self.partner_id.name)
        config = self.partner_id.invoice_import_id
        if config.invoice_line_method.startswith('1line'):
            if config.invoice_line_method == '1line_no_product':
                il_vals = {
                    'account_id': config.account_id.id,
                    'invoice_line_tax_id': config.tax_ids.ids or False,
                    'price_unit': parsed_inv.get('amount_untaxed'),
                    }
            elif config.invoice_line_method == '1line_static_product':
                product = config.static_product_id
                il_vals = ailo.product_id_change(
                    product.id, product.uom_id.id, type='in_invoice',
                    partner_id=self.partner_id.id,
                    fposition_id=self.partner_id.property_account_position.id,
                    company_id=company.id)['value']
                il_vals.update({
                    'product_id': product.id,
                    'price_unit': parsed_inv.get('amount_untaxed'),
                    })
            if config.label:
                il_vals['name'] = config.label
            elif parsed_inv.get('description'):
                il_vals['name'] = parsed_inv['description']
            elif not il_vals.get('name'):
                il_vals['name'] = _('MISSING DESCRIPTION')
            self.set_1line_price_unit_and_quantity(il_vals, parsed_inv)
            vals['invoice_line'].append((0, 0, il_vals))
        elif config.invoice_line_method.startswith('nline'):
            if not parsed_inv.get('lines'):
                raise UserError(_(
                    "You have selected a Multi Line method for this import "
                    "but Odoo could not extract/read any XML file inside "
                    "the PDF invoice."))
            if config.invoice_line_method == 'nline_no_product':
                static_vals = {
                    'account_id': config.account_id.id,
                    'invoice_line_tax_id': config.tax_ids.ids or False,
                    }
            elif config.invoice_line_method == 'nline_static_product':
                sproduct = config.static_product_id
                static_vals = ailo.product_id_change(
                    sproduct.id, sproduct.uom_id.id, type='in_invoice',
                    partner_id=self.partner_id.id,
                    fposition_id=self.partner_id.property_account_position.id,
                    company_id=company.id)['value']
                static_vals['product_id'] = sproduct.id
            else:
                static_vals = {}
            for line in parsed_inv['lines']:
                il_vals = static_vals.copy()
                if config.invoice_line_method == 'nline_auto_product':
                    product = self._match_product(line)
                    fposition_id = self.partner_id.property_account_position.id
                    il_vals.update(
                        ailo.product_id_change(
                            product.id, product.uom_id.id, type='in_invoice',
                            partner_id=self.partner_id.id,
                            fposition_id=fposition_id,
                            company_id=company.id)['value'])
                    il_vals['product_id'] = product.id
                if line.get('name'):
                    il_vals['name'] = line['name']
                elif not il_vals.get('name'):
                    il_vals['name'] = _('MISSING DESCRIPTION')
                il_vals.update({
                    'quantity': line['quantity'],
                    'price_unit': line['price_unit'],
                    })
                vals['invoice_line'].append((0, 0, il_vals))
        # Write analytic account + fix syntax for taxes
        aacount_id = config.account_analytic_id.id or False
        for line in vals['invoice_line']:
            line_dict = line[2]
            if line_dict.get('invoice_line_tax_id'):
                line_dict['invoice_line_tax_id'] = [
                    (6, 0, line_dict['invoice_line_tax_id'])]
            if aacount_id:
                line_dict['account_analytic_id'] = aacount_id
        return vals

    @api.model
    def _match_product(self, parsed_line):
        """This method is designed to be inherited"""
        ppo = self.env['product.product']
        if parsed_line.get('ean13'):
            # Don't filter on purchase_ok = 1 because we don't depend
            # on the purchase module
            products = ppo.search([('ean13', '=', parsed_line['ean13'])])
            if products:
                return products[0]
            elif parsed_line.get('product_code'):
                # Should probably be modified to match via the supplier code
                products = ppo.search(
                    [('default_code', '=', parsed_line['product_code'])])
                if products:
                    return products[0]
        raise UserError(_(
            "Could not find any corresponding product in the Odoo database "
            "with EAN13 '%s' or Default Code '%s'.")
            % (parsed_line.get('ean13'), parsed_line.get('product_code')))

    @api.model
    def set_1line_price_unit_and_quantity(self, il_vals, parsed_inv):
        """For the moment, we only take into account the 'price_include'
        option of the first tax"""
        il_vals['quantity'] = 1
        il_vals['price_unit'] = parsed_inv.get('amount_total')
        if il_vals.get('invoice_line_tax_id'):
            first_tax = self.env['account.tax'].browse(
                il_vals['invoice_line_tax_id'][0])
            if not first_tax.price_include:
                il_vals['price_unit'] = parsed_inv.get('amount_untaxed')

    @api.model
    def _get_currency(self, parsed_inv):
        currency = False
        if parsed_inv.get('currency_iso'):
            currency_iso = parsed_inv['currency_iso'].upper()
            currencies = self.env['res.currency'].search(
                [('name', '=', currency_iso)])
            if currencies:
                currency = currencies[0]
            else:
                raise UserError(_(
                    "The analysis of the PDF invoice returned '%s' as "
                    "the currency ISO code. But there are no currency "
                    "with that name in Odoo.") % currency_iso)
        if not currency and parsed_inv.get('currency_symbol'):
            cur_symbol = parsed_inv['currency_symbol']
            currencies = self.env['res.currency'].search(
                [('symbol', '=', cur_symbol)])
            if currencies:
                currency = currencies[0]
            else:
                raise UserError(_(
                    "The analysis of the PDF invoice returned '%s' as "
                    "the currency symbol. But there are no currency "
                    "with that symbol in Odoo.") % cur_symbol)
        if not currency:
            currency = self.env.user.company_id.currency_id
        return currency

    @api.multi
    def parse_invoice(self):
        self.ensure_one()
        file_data = base64.b64decode(self.pdf_file)
        parsed_inv = {}
        try:
            parsed_inv = self.parse_invoice_with_embedded_xml(file_data)
        except:
            pass
        if not parsed_inv:
            parsed_inv = self.parse_invoice_with_invoice2data(file_data)
        prec_ac = self.env['decimal.precision'].precision_get('Account')
        prec_pp = self.env['decimal.precision'].precision_get('Product Price')
        prec_uom = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if parsed_inv['amount_total'] < 0:
            parsed_inv['type'] = 'in_refund'
        else:
            parsed_inv['type'] = 'in_invoice'
        for entry in ['amount_untaxed', 'amount_total']:
            parsed_inv[entry] = float_round(
                parsed_inv[entry], precision_digits=prec_ac)
            if parsed_inv['type'] == 'in_refund':
                parsed_inv[entry] *= -1
        if parsed_inv.get('lines'):
            for line in parsed_inv['lines']:
                line['quantity'] = float_round(
                    line['quantity'], precision_digits=prec_uom)
                line['price_unit'] = float_round(
                    line['price_unit'], precision_digits=prec_pp)
                if parsed_inv['type'] == 'in_refund':
                    line['quantity'] *= -1
        logger.debug('Resulf of invoice parsing parsed_inv=%s', parsed_inv)
        return parsed_inv

    @api.multi
    def import_invoice(self):
        self.ensure_one()
        logger.info('Starting to import PDF invoice')
        aio = self.env['account.invoice']
        iaao = self.env['ir.actions.act_window']
        parsed_inv = self.parse_invoice()
        partner = self._select_partner(parsed_inv)
        currency = self._get_currency(parsed_inv)
        self.write({
            'partner_id': partner.id,
            'currency_id': currency.id,
            'amount_untaxed': parsed_inv['amount_untaxed'],
            'amount_total': parsed_inv['amount_total'],
            })
        if not self.partner_id.invoice_import_id:
            raise UserError(_(
                "Missing Invoice Import Configuration on partner %s")
                % self.partner_id.name)
        domain = [
            ('commercial_partner_id', '=', self.partner_id.id),
            ('type', 'in', ('in_invoice', 'in_refund'))]
        existing_invs = aio.search(
            domain +
            [(
                'supplier_invoice_number',
                '=ilike',
                parsed_inv.get('invoice_number'))])
        if existing_invs:
            raise UserError(_(
                "This invoice has already been created in Odoo. It's "
                "Supplier Invoice Number is '%s' and it's Odoo number "
                "is '%s'")
                % (parsed_inv.get('invoice_number'), existing_invs[0].number))
        draft_same_supplier_invs = aio.search(
            domain + [('state', '=', 'draft')])
        logger.debug('draft_same_supplier_invs=%s', draft_same_supplier_invs)
        if draft_same_supplier_invs:
            action = iaao.for_xml_id(
                'account_invoice_pdf_import',
                'account_invoice_pdf_import_action')
            default_invoice_id = False
            if len(draft_same_supplier_invs) == 1:
                default_invoice_id = draft_same_supplier_invs[0].id
            self.write({
                'state': 'update',
                'invoice_id': default_invoice_id,
            })
            action['res_id'] = self.id
            action['context'] = {'parsed_inv': parsed_inv}
            return action
        else:
            action = self.with_context(parsed_inv=parsed_inv).create_invoice()
            return action

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        aio = self.env['account.invoice']
        iaao = self.env['ir.actions.act_window']
        assert self._context.get('parsed_inv'), 'Missing parsed_invoice'
        parsed_inv = self._context['parsed_inv']
        vals = self._prepare_create_invoice_vals(parsed_inv)
        logger.debug('Invoice vals for creation: %s', vals)
        invoice = aio.create(vals)
        logger.info('Invoice ID %d created from PDF', invoice.id)
        invoice.button_reset_taxes()

        # Force tax amount if necessary
        prec = self.env['decimal.precision'].precision_get('Account')
        if (
                parsed_inv.get('amount_total') and
                parsed_inv.get('amount_untaxed') and
                float_compare(
                    invoice.amount_total,
                    parsed_inv['amount_total'],
                    precision_digits=prec)):
            raise UserError(_(
                "The total amount is different from the untaxed amount, "
                "but no tax has been configured !"))
            initial_tax_amount = invoice.tax_line[0].amount
            tax_amount = parsed_inv['amount_total'] -\
                parsed_inv['amount_untaxed']
            invoice.tax_line[0].amount = tax_amount
            cur_symbol = invoice.currency_id.symbol
            invoice.message_post(
                'The total tax amount has been forced to %s %s '
                '(amount computed by Odoo was: %s %s).'
                % (tax_amount, cur_symbol, initial_tax_amount, cur_symbol))
        # Attach PDF to invoice
        self.env['ir.attachment'].create({
            'name': self.pdf_filename,
            'res_id': invoice.id,
            'res_model': 'account.invoice',
            'datas': self.pdf_file,
            })
        invoice.message_post(_(
            "This invoice has been created automatically via PDF import"))
        if parsed_inv.get('chatter_msg'):
            invoice.message_post(parsed_inv['chatter_msg'])
        action = iaao.for_xml_id('account', 'action_invoice_tree2')
        action.update({
            'view_mode': 'form,tree,calendar,graph',
            'views': False,
            'res_id': invoice.id,
            })
        return action

    @api.model
    def _prepare_update_invoice_vals(self, parsed_inv):
        vals = {
            'supplier_invoice_number':
            parsed_inv.get('invoice_number'),
            'date_invoice': parsed_inv.get('date'),
            'check_total': parsed_inv.get('amount_total'),
        }
        if parsed_inv.get('date_due'):
            vals['date_due'] = parsed_inv['date_due']
        return vals

    @api.multi
    def update_invoice(self):
        self.ensure_one()
        iaao = self.env['ir.actions.act_window']
        if not self.invoice_id:
            raise UserError(_(
                'You must select a supplier invoice or refund to update'))
        assert self._context.get('parsed_inv'), 'Missing parsed_invoice'
        parsed_inv = self._context['parsed_inv']
        # When invoice with embedded XML files will be more widely used,
        # we should also update invoice lines
        vals = self._prepare_update_invoice_vals(parsed_inv)
        logger.debug('Updating supplier invoice with vals=%s', vals)
        self.invoice_id.write(vals)
        self.env['ir.attachment'].create({
            'name': self.pdf_filename,
            'res_id': self.invoice_id.id,
            'res_model': 'account.invoice',
            'datas': self.pdf_file,
            })
        logger.info('Supplier invoice ID %d updated', self.invoice_id.id)
        self.invoice_id.message_post(_(
            "This invoice has been updated automatically via PDF import"))
        action = iaao.for_xml_id('account', 'action_invoice_tree2')
        action.update({
            'view_mode': 'form,tree,calendar,graph',
            'views': False,
            'res_id': self.invoice_id.id,
            })
        return action
