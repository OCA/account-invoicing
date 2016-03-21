# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Invoice Import UBL module for Odoo
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
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
from openerp.exceptions import Warning as UserError
from openerp.tools import float_compare
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AccountInvoiceImport(models.TransientModel):
    _inherit = 'account.invoice.import'

    @api.model
    def parse_xml_invoice(self, xml_root):
        if (
                xml_root.tag and
                xml_root.tag.startswith(
                '{urn:oasis:names:specification:ubl:schema:xsd:Invoice')):
            return self.parse_ubl_xml(xml_root)
        else:
            return super(AccountInvoiceImport, self).parse_xml_invoice(
                xml_root)

    @api.model
    def ubl_select_taxes_of_invoice_line(
            self, taxes_xpath, namespaces, unece2odoo_tax, line_name=False):
        '''This method is designed to be inherited'''
        tax_ids = []
        prec = self.env['decimal.precision'].precision_get('Account')
        for tax in taxes_xpath:
            type_code_xpath = tax.xpath(
                "cac:TaxScheme/cbc:ID[@schemeAgencyID='6']",
                namespaces=namespaces)
            type_code = type_code_xpath and type_code_xpath[0].text or 'VAT'
            categ_code_xpath = tax.xpath(
                "cbc:ID", namespaces=namespaces)
            # TODO: Understand why sometimes they use H
            categ_code = categ_code_xpath and categ_code_xpath[0].text or False
            if categ_code == 'H':
                categ_code = 'S'
            percent_xpath = tax.xpath(
                "cbc:Percent", namespaces=namespaces)
            percent = percent_xpath[0].text and float(percent_xpath[0].text)\
                or 0.0
            odoo_tax_found = False
            for otax in unece2odoo_tax:
                if (
                        otax['unece_type_code'] == type_code and
                        otax['type'] == 'percent' and
                        not float_compare(
                            percent, otax['amount'], precision_digits=prec)):
                    if categ_code and categ_code != otax['unece_categ_code']:
                        continue
                    tax_ids.append(otax['id'])
                    odoo_tax_found = True
                    break
            if not odoo_tax_found:
                raise UserError(_(
                    "No tax in Odoo matched the tax "
                    "described in the XML file as Type Code = %s, "
                    "Category Code = %s and Percentage = %s "
                    "(related to: %s)") % (
                        type_code, categ_code, percent,
                        line_name))
        return tax_ids

    @api.model
    def parse_ubl_xml(self, xml_root):
        """Parse UBL Invoice XML file"""
        namespaces = xml_root.nsmap
        prec = self.env['decimal.precision'].precision_get('Account')
        logger.debug('XML file namespaces=%s', namespaces)
        namespaces.pop(None)
        doc_type_xpath = xml_root.xpath(
            "//cbc:InvoiceTypeCode[@listAgencyID='6']", namespaces=namespaces)
        if doc_type_xpath and doc_type_xpath[0].text != '380':
            raise UserError(_(
                "This UBL XML file is not an invoice/refund file "
                "(TypeCode is %s") % doc_type_xpath[0].text)
        inv_number_xpath = xml_root.xpath('//cbc:ID', namespaces=namespaces)
        supplier_xpath = xml_root.xpath(
            '//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name',
            namespaces=namespaces)
        vat_xpath = xml_root.xpath(
            '//cac:AccountingSupplierParty/cac:Party'
            '/cac:PartyTaxScheme/cbc:CompanyID',
            namespaces=namespaces)
        email_xpath = xml_root.xpath(
            "//cac:AccountingSupplierParty/cac:Party"
            "/cac:Contact/cbc:ElectronicMail",
            namespaces=namespaces)
        date_xpath = xml_root.xpath(
            '//cbc:IssueDate', namespaces=namespaces)
        date_dt = datetime.strptime(date_xpath[0].text, '%Y-%m-%d')
        date_due_xpath = xml_root.xpath(
            "//cbc:PaymentDueDate", namespaces=namespaces)
        date_due_str = False
        if date_due_xpath:
            date_due_dt = datetime.strptime(date_due_xpath[0].text, '%Y-%m-%d')
            date_due_str = fields.Date.to_string(date_due_dt)
        currency_iso_xpath = xml_root.xpath(
            "//cbc:DocumentCurrencyCode", namespaces=namespaces)
        total_untaxed_xpath = xml_root.xpath(
            "//cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount",
            namespaces=namespaces)
        amount_untaxed = float(total_untaxed_xpath[0].text)
        total_line_xpath = xml_root.xpath(
            "//cac:LegalMonetaryTotal/cbc:LineExtensionAmount",
            namespaces=namespaces)
        if total_line_xpath:
            total_line = float(total_line_xpath[0].text)
        else:
            total_line = amount_untaxed
        amount_total_xpath = xml_root.xpath(
            "//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount",
            namespaces=namespaces)
        if amount_total_xpath:
            amount_total = float(amount_total_xpath[0].text)
        else:
            payable_total = xml_root.xpath(
                "//cac:LegalMonetaryTotal/cbc:PayableAmount",
                namespaces=namespaces)
            amount_total = float(payable_total[0].text)
        payment_type_code = xml_root.xpath(
            "//cbc:PaymentMeansCode[@listAgencyID='6']",
            namespaces=namespaces)
        iban_xpath = bic_xpath = False
        if payment_type_code and payment_type_code[0].text == '31':
            iban_xpath = xml_root.xpath(
                "//cac:PayeeFinancialAccount/cbc:ID[@schemeID='IBAN']",
                namespaces=namespaces)
            bic_xpath = xml_root.xpath(
                "//cac:PayeeFinancialAccount"
                "/cac:FinancialInstitutionBranch"
                "/cac:FinancialInstitution"
                "/cbc:ID[@schemeID='BIC']",
                namespaces=namespaces)
        uoms = self.env['product.uom'].search([('unece_code', '!=', False)])
        unece2odoo_uom = {}
        for uom in uoms:
            unece2odoo_uom[uom.unece_code] = uom.id
        logger.debug('unece2odoo_uom = %s', unece2odoo_uom)
        taxes = self.env['account.tax'].search([
            ('unece_type_id', '!=', False),
            ('unece_categ_id', '!=', False),
            ('type_tax_use', 'in', ('all', 'purchase')),
            ('price_include', '=', False),  # TODO : check what the standard
            ])                              # says about this
        unece2odoo_tax = []
        for tax in taxes:
            unece2odoo_tax.append({
                'unece_type_code': tax.unece_type_code,
                'unece_categ_code': tax.unece_categ_code,
                'type': tax.type,
                'amount': tax.amount * 100,
                'id': tax.id,
                })
        logger.debug('unece2odoo_tax=%s', unece2odoo_tax)
        res_lines = []
        total_line_lines = 0.0
        inv_line_xpath = xml_root.xpath(
            "//cac:InvoiceLine", namespaces=namespaces)
        for iline in inv_line_xpath:
            price_unit_xpath = iline.xpath(
                "cac:Price/cbc:PriceAmount", namespaces=namespaces)
            qty_xpath = iline.xpath(
                "cbc:InvoicedQuantity", namespaces=namespaces)
            if not qty_xpath:
                continue
            qty = float(qty_xpath[0].text)
            if not qty:
                qty = 1
            uos_id = False
            if qty_xpath[0].attrib and qty_xpath[0].attrib.get('unitCode'):
                unece_uom = qty_xpath[0].attrib['unitCode']
                if unece_uom == 'ZZ':
                    unece_uom = 'C62'
                uos_id = unece2odoo_uom.get(unece_uom)
            ean13_xpath = iline.xpath(
                "cac:Item"
                "/cac:StandardItemIdentification"
                "/cbc:ID[@schemeID='GTIN']",
                namespaces=namespaces)
            product_code_xpath = iline.xpath(
                "cac:Item/cac:SellersItemIdentification/cbc:ID",
                namespaces=namespaces)
            name_xpath = iline.xpath(
                "cac:Item/cbc:Description", namespaces=namespaces)
            name = name_xpath and name_xpath[0].text or '-'
            price_subtotal_xpath = iline.xpath(
                "cbc:LineExtensionAmount", namespaces=namespaces)
            price_subtotal = float(price_subtotal_xpath[0].text)
            if not price_subtotal:
                continue
            if price_unit_xpath:
                price_unit = float(price_unit_xpath[0].text)
            else:
                price_unit = price_subtotal / qty
            total_line_lines += price_subtotal
            taxes_xpath = iline.xpath(
                "cac:Item/cac:ClassifiedTaxCategory", namespaces=namespaces)
            if not taxes_xpath:
                taxes_xpath = iline.xpath(
                    "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory",
                    namespaces=namespaces)
            tax_ids = self.ubl_select_taxes_of_invoice_line(
                taxes_xpath, namespaces, unece2odoo_tax, name)
            vals = {
                'ean13': ean13_xpath and ean13_xpath[0].text or False,
                'product_code':
                product_code_xpath and product_code_xpath[0].text or False,
                'quantity': qty,
                'uos_id': uos_id,
                'price_unit': price_unit,
                'name': name,
                'tax_ids': tax_ids,
                }
            res_lines.append(vals)

        if float_compare(
                total_line, total_line_lines, precision_digits=prec):
            logger.warning(
                "The gloabl LineExtensionAmount (%s) doesn't match the "
                "sum of the amounts of each line (%s). It can "
                "have a diff of a few cents due to sum of rounded values vs "
                "rounded sum policies.", total_line, total_line_lines)

        res = {
            'vat': vat_xpath and vat_xpath[0].text or False,
            'partner_name': supplier_xpath[0].text,
            'partner_email': email_xpath and email_xpath[0].text or False,
            'invoice_number': inv_number_xpath[0].text,
            'date': fields.Date.to_string(date_dt),
            'date_due': date_due_str,
            'currency_iso': currency_iso_xpath[0].text,
            'amount_total': amount_total,
            'amount_untaxed': amount_untaxed,
            'iban': iban_xpath and iban_xpath[0].text or False,
            'bic': bic_xpath and bic_xpath[0].text or False,
            'lines': res_lines,
            }
        # Hack for the sample UBL invoices that use an invalid VAT number
        if res['vat'] == 'NL123456789B01':
            res.pop('vat')
        # and invalid IBAN
        if res['iban'] == 'NL23ABNA0123456789':
            res.pop('iban')
        logger.info('Result of UBL XML parsing: %s', res)
        return res
