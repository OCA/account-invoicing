# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.tools import float_compare
from openerp.exceptions import Warning as UserError
import PyPDF2
from lxml import etree
from StringIO import StringIO
import mimetypes
import logging

logger = logging.getLogger(__name__)


class BusinessDocumentImport(models.AbstractModel):
    _name = 'business.document.import'
    _description = 'Common methods to import business documents'

    @api.model
    def _match_partner(
            self, partner_dict, chatter_msg, partner_type='supplier'):
        rpo = self.env['res.partner']
        if partner_dict.get('recordset'):
            return partner_dict['recordset']
        if partner_dict.get('id'):
            return rpo.browse(partner_dict['id'])
        if partner_type == 'supplier':
            domain = [('supplier', '=', True)]
            partner_type_label = _('supplier')
        elif partner_type == 'customer':
            domain = [('customer', '=', True)]
            partner_type_label = _('customer')
        else:
            domain = []
            partner_type_label = _('partner')
        if partner_dict.get('vat'):
            vat = partner_dict['vat'].replace(' ', '').upper()
            # use base_vat_sanitized
            partners = rpo.search(
                domain + [
                    ('parent_id', '=', False),
                    ('sanitized_vat', '=', vat)])
            if partners:
                return partners[0]
            else:
                raise UserError(_(
                    "The analysis of the business document returned '%s' as "
                    "%s VAT number. But there are no %s "
                    "with this VAT number in Odoo.")
                    % (vat, partner_type_label, partner_type_label))
        if partner_dict.get('email') and '@' in partner_dict['email']:
            partners = rpo.search(
                domain + [('email', '=ilike', partner_dict['email'])])
            if partners:
                return partners[0]
            else:
                partner_domain_name = partner_dict['email'].split('@')[1]
                partners = rpo.search(
                    domain +
                    [('website', '=ilike', '%' + partner_domain_name)])
                # I can't search on email addresses with partner_domain_name
                # because of the emails such as @gmail.com, @yahoo.com that may
                # match random partners
                if partners:
                    chatter_msg.append(_(
                        "The %s has been identified by the domain name of "
                        "the email address '%s', so please check carefully "
                        "that the %s is correct.") % (
                            partner_type_label,
                            partner_dict['email'],
                            partner_type_label))
                    return partners[0]
        if partner_dict.get('name'):
            partners = rpo.search(
                domain + [
                    ('name', '=ilike', partner_dict['name']),
                    ('is_company', '=', True),
                    ])
            if partners:
                return partners[0]
        raise UserError(_(
            "Odoo couldn't find any %s corresponding to the following "
            "information extracted from the business document:\n"
            "VAT number: %s\n"
            "E-mail: %s\n"
            "Name: %s\n")
            % (
                partner_type_label,
                partner_dict.get('vat'),
                partner_dict.get('email'),
                partner_dict.get('name')))

    @api.model
    def _match_product(self, product_dict, chatter_msg, partner=False):
        """This method is designed to be inherited"""
        ppo = self.env['product.product']
        if product_dict.get('recordset'):
            return product_dict['recordset']
        if product_dict.get('id'):
            return ppo.browse(product_dict['id'])
        if product_dict.get('ean13'):
            products = ppo.search([
                ('ean13', '=', product_dict['ean13'])])
            if products:
                return products[0]
        if product_dict.get('code'):
            products = ppo.search([
                '|',
                ('ean13', '=', product_dict['code']),
                ('default_code', '=', product_dict['code'])])
            if products:
                return products[0]
            # WARNING: Won't work for multi-variant products
            # because product.supplierinfo is attached to product template
            if partner:
                sinfo = self.env['product.supplierinfo'].search([
                    ('name', '=', partner.id),
                    ('product_code', '=', product_dict['code']),
                    ])
                if (
                        sinfo and
                        sinfo[0].product_tmpl_id.product_variant_ids and
                        len(
                        sinfo[0].product_tmpl_id.product_variant_ids) == 1
                        ):
                    return sinfo[0].product_tmpl_id.product_variant_ids[0]
        raise UserError(_(
            "Odoo couldn't find any product corresponding to the "
            "following information extracted from the business document: "
            "EAN13: %s\n"
            "Product code: %s\n"
            "Supplier: %s\n") % (
                product_dict.get('ean13'),
                product_dict.get('code'),
                partner and partner.name or 'None'))

    @api.model
    def _match_currency(self, currency_dict, chatter_msg):
        if not currency_dict:
            currency_dict = {}
        rco = self.env['res.currency']
        if currency_dict.get('recordset'):
            return currency_dict['recordset']
        if currency_dict.get('id'):
            return rco.browse(currency_dict['id'])
        if currency_dict.get('iso'):
            currency_iso = currency_dict['iso'].upper()
            currencies = rco.search(
                [('name', '=', currency_iso)])
            if currencies:
                return currencies[0]
            else:
                raise UserError(_(
                    "The analysis of the business document returned '%s' as "
                    "the currency ISO code. But there are no currency "
                    "with that code in Odoo.") % currency_iso)
        if currency_dict.get('symbol'):
            currencies = rco.search(
                [('symbol', '=', currency_dict['symbol'])])
            if currencies:
                return currencies[0]
            else:
                raise UserError(_(
                    "The analysis of the business document returned '%s' as "
                    "the currency symbol. But there are no currency "
                    "with that symbol in Odoo.") % currency_dict['symbol'])
        if currency_dict.get('iso_or_symbol'):
            currencies = rco.search([
                '|',
                ('name', '=', currency_dict['iso_or_symbol'].upper()),
                ('symbol', '=', currency_dict['iso_or_symbol'])])
            if currencies:
                return currencies[0]
            else:
                raise UserError(_(
                    "The analysis of the business document returned '%s' as "
                    "the currency symbol or ISO code. But there are no "
                    "currency with the symbol nor ISO code in Odoo.")
                    % currency_dict['iso_or_symbol'])
        if currency_dict.get('country_code'):
            country_code = currency_dict['country_code'].upper()
            countries = self.env['res.country'].search([
                ('code', '=', country_code)])
            if countries:
                country = countries[0]
                if country.currency_id:
                    return country.currency_id
                else:
                    raise UserError(_(
                        "The analysis of the business document returned '%s' "
                        "as the country code to find the related currency. "
                        "But the country '%s' doesn't have any related "
                        "currency configured in Odoo.")
                        % (country_code, country.name))
            else:
                raise UserError(_(
                    "The analysis of the business document returned '%s' "
                    "as the country code to find the related currency. "
                    "But there is no country with that code in Odoo.")
                    % country_code)
        company_cur = self.env.user.company_id.currency_id
        chatter_msg.append(_(
            'No currency specified, so Odoo used the company currency (%s)')
            % company_cur.name)
        return company_cur

    @api.model
    def _match_uom(self, uom_dict, chatter_msg, product=False):
        puo = self.env['product.uom']
        if not uom_dict:
            uom_dict = {}
        if uom_dict.get('recordset'):
            return uom_dict['recordset']
        if uom_dict.get('id'):
            return puo.browse(uom_dict['id'])
        if uom_dict.get('unece_code'):
            uoms = puo.search([
                ('unece_code', '=', uom_dict['unece_code'])])
            if uoms:
                return uoms[0]
            else:
                chatter_msg.append(_(
                    "The analysis of the business document returned '%s' "
                    "as the unit of measure UNECE code, but there is no "
                    "unit of measure with that UNECE code in Odoo. Please "
                    "check the configuration of the units of measures in "
                    "Odoo.") % uom_dict['unece_code'])
        if uom_dict.get('name'):
            uoms = puo.search([
                ('name', '=ilike', uom_dict['name'] + '%')])
            if uoms:
                return uoms[0]
        if product:
            return product.uom_id
        chatter_msg.append(_(
            "<p>Odoo couldn't find any unit of measure corresponding to the "
            "following information extracted from the business document:</p>"
            "<ul><li>UNECE code: %s</li>"
            "<li>Name of the unit of measure: %s</li></ul>"
            "<p>So the unit of measure 'Unit(s)' has been used. <em>You may "
            "have to change it manually.</em></p>")
            % (uom_dict.get('unece_code'), uom_dict.get('name')))
        return self.env.ref('product.product_uom_unit')

    @api.model
    def _match_taxes(
            self, taxes_list, chatter_msg,
            type_tax_use='purchase', price_include=False):
        """taxes_list must be a list of tax_dict"""
        taxes_recordset = self.env['account.tax'].browse(False)
        for tax_dict in taxes_list:
            taxes_recordset += self._match_tax(
                tax_dict, chatter_msg, type_tax_use=type_tax_use,
                price_include=price_include)
        return taxes_recordset

    @api.model
    def _match_tax(
            self, tax_dict, chatter_msg,
            type_tax_use='purchase', price_include=False):
        """Example:
        tax_dict = {
            'type': 'percent',  # required param, 'fixed' or 'percent'
            'amount': 20.0,  # required
            'unece_type_code': 'VAT',
            'unece_categ_code': 'S',
            }
        With l10n_fr, it will return 20% VAT tax.
        """
        ato = self.env['account.tax']
        if tax_dict.get('recordset'):
            return tax_dict['recordset']
        if tax_dict.get('id'):
            return ato.browse(tax_dict['id'])
        domain = []
        prec = self.env['decimal.precision'].precision_get('Account')
        # we should not use the Account prec directly, but...
        if type_tax_use == 'purchase':
            domain.append(('type_tax_use', 'in', ('purchase', 'all')))
        elif type_tax_use == 'sale':
            domain.append(('type_tax_use', 'in', ('sale', 'all')))
        if price_include is False:
            domain.append(('price_include', '=', False))
        elif price_include is True:
            domain.append(('price_include', '=', True))
        # with the code abose, if you set price_include=None, it will
        # won't depend on the value of the price_include parameter
        assert tax_dict.get('type') in ['fixed', 'percent'], 'bad tax type'
        assert 'amount' in tax_dict, 'Missing amount key in tax_dict'
        domain.append(('type', '=', tax_dict['type']))
        if tax_dict.get('unece_type_code'):
            domain.append(
                ('unece_type_code', '=', tax_dict['unece_type_code']))
        if tax_dict.get('unece_categ_code'):
            domain.append(
                ('unece_categ_code', '=', tax_dict['unece_categ_code']))
        taxes = ato.search(domain)
        for tax in taxes:
            tax_amount = tax.amount
            if tax_dict['type'] == 'percent':
                tax_amount *= 100
            if not float_compare(
                    tax_dict['amount'], tax_amount, precision_digits=prec):
                return tax
        raise UserError(_(
            "Odoo couldn't find any tax with 'Tax Application' = '%s' "
            "and 'Tax Included in Price' = '%s' which correspond to the "
            "following information extracted from the business document:\n"
            "UNECE Tax Type code: %s\n"
            "UNECE Tax Category code: %s\n"
            "Tax amount: %s %s") % (
                type_tax_use,
                price_include,
                tax_dict.get('unece_type_code'),
                tax_dict.get('unece_categ_code'),
                tax_dict['amount'],
                tax_dict['type'] == 'percent' and '%' or _('(fixed)')))

    def get_xml_files_from_pdf(self, pdf_file):
        """Returns a dict with key = filename, value = XML file obj"""
        logger.info('Trying to find an embedded XML file inside PDF')
        res = {}
        try:
            fd = StringIO(pdf_file)
            pdf = PyPDF2.PdfFileReader(fd)
            logger.debug('pdf.trailer=%s', pdf.trailer)
            pdf_root = pdf.trailer['/Root']
            logger.debug('pdf_root=%s', pdf_root)
            embeddedfiles = pdf_root['/Names']['/EmbeddedFiles']['/Names']
            i = 0
            xmlfiles = {}  # key = filename, value = PDF obj
            for embeddedfile in embeddedfiles[:-1]:
                mime_res = mimetypes.guess_type(embeddedfile)
                if mime_res and mime_res[0] == 'application/xml':
                    xmlfiles[embeddedfile] = embeddedfiles[i+1]
                i += 1
            logger.debug('xmlfiles=%s', xmlfiles)
            for filename, xml_file_dict_obj in xmlfiles.iteritems():
                try:
                    xml_file_dict = xml_file_dict_obj.getObject()
                    logger.debug('xml_file_dict=%s', xml_file_dict)
                    xml_string = xml_file_dict['/EF']['/F'].getData()
                    xml_root = etree.fromstring(xml_string)
                    logger.debug(
                        'A valid XML file %s has been found in the PDF file',
                        filename)
                    res[filename] = xml_root
                except:
                    continue
        except:
            pass
        logger.info('Valid XML files found in PDF: %s', res.keys())
        return res
