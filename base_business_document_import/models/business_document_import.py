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
    def _strip_cleanup_dict(self, match_dict):
        if match_dict:
            for key, value in match_dict.iteritems():
                if value and isinstance(value, (str, unicode)):
                    match_dict[key] = value.strip()
            if match_dict.get('country_code'):
                match_dict['country_code'] = match_dict['country_code'].upper()
            if match_dict.get('state_code'):
                match_dict['state_code'] = match_dict['state_code'].upper()

    @api.model
    def _match_partner(
            self, partner_dict, chatter_msg, partner_type='supplier'):
        """Example:
        partner_dict = {
            'country_code': 'FR',
            'state_code': False,
            'vat': 'FR12448890432',
            'email': 'roger.lemaire@akretion.com',
            'name': 'Akretion France',
            'ref': 'C1242',
            'phone': '01.41.98.12.42',
            'fax': '01.41.98.12.43',
            }
        The keys 'phone' and 'fax' are used by the module
        base_phone_business_document_import
        """
        rpo = self.env['res.partner']
        self._strip_cleanup_dict(partner_dict)
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
        country = False
        if partner_dict.get('country_code'):
            countries = self.env['res.country'].search([
                ('code', '=', partner_dict['country_code'])])
            if countries:
                country = countries[0]
                domain += [
                    '|',
                    ('country_id', '=', False),
                    ('country_id', '=', country.id)]
            else:
                chatter_msg.append(_(
                    "The analysis of the business document returned '%s' as "
                    "country code. But there are no country with that code "
                    "in Odoo.") % partner_dict['country_code'])
        if country and partner_dict.get('state_code'):
            states = self.env['res.country.state'].search([
                ('code', '=', partner_dict['state_code']),
                ('country_id', '=', country.id)])
            if states:
                domain += [
                    '|',
                    ('state_id', '=', False),
                    ('state_id', '=', states[0].id)]
        # Hook to plug alternative matching methods
        partner = self._hook_match_partner(
            partner_dict, chatter_msg, domain, partner_type_label)
        if partner:
            return partner
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
                chatter_msg.append(_(
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
                if partner_domain_name:
                    partners = rpo.search(
                        domain +
                        [('website', '=ilike', '%' + partner_domain_name)])
                    # I can't search on email addresses with
                    # partner_domain_name because of the emails such as
                    # @gmail.com, @yahoo.com that may match random partners
                    if partners:
                        chatter_msg.append(_(
                            "The %s has been identified by the domain name of "
                            "the email address '%s', so please check "
                            "carefully that the %s is correct.") % (
                                partner_type_label,
                                partner_dict['email'],
                                partner_type_label))
                        return partners[0]
        if partner_dict.get('ref'):
            partners = rpo.search(
                domain + [('ref', '=', partner_dict['ref'])])
            if partners:
                return partners[0]
        if partner_dict.get('name'):
            partners = rpo.search(
                domain + [('name', '=ilike', partner_dict['name'])])
            if partners:
                return partners[0]
        raise UserError(_(
            "Odoo couldn't find any %s corresponding to the following "
            "information extracted from the business document:\n"
            "Country code: %s\n"
            "State code: %s\n"
            "VAT number: %s\n"
            "E-mail: %s\n"
            "Reference: %s\n"
            "Name: %s\n")
            % (
                partner_type_label,
                partner_dict.get('country_code'),
                partner_dict.get('state_code'),
                partner_dict.get('vat'),
                partner_dict.get('email'),
                partner_dict.get('ref'),
                partner_dict.get('name')))

    @api.model
    def _hook_match_partner(
            self, partner_dict, chatter_msg, domain, partner_type_label):
        return False

    @api.model
    def _match_shipping_partner(self, shipping_dict, partner, chatter_msg):
        """Example:
        shipping_dict = {
            'partner': {
                'email': 'contact@akretion.com',
                'name': 'Akretion France',
                },
            'address': {
                'zip': '69100',
                'country_code': 'FR',
                },
            }
        The partner argument is a bit special: it is a fallback in case
        shipping_dict['partner'] = {}
        """
        rpo = self.env['res.partner']
        if shipping_dict.get('partner'):
            partner = self._match_partner(
                shipping_dict['partner'], chatter_msg, partner_type=False)
        domain = [('parent_id', '=', partner.id)]
        address_dict = shipping_dict['address']
        self._strip_cleanup_dict(address_dict)
        country = False
        if address_dict.get('country_code'):
            countries = self.env['res.country'].search([
                ('code', '=', address_dict['country_code'])])
            if countries:
                country = countries[0]
                domain += [
                    '|',
                    ('country_id', '=', False),
                    ('country_id', '=', country.id)]
            else:
                chatter_msg.append(_(
                    "The analysis of the business document returned '%s' as "
                    "country code. But there are no country with that code "
                    "in Odoo.") % address_dict['country_code'])
        if country and address_dict.get('state_code'):
            states = self.env['res.country.state'].search([
                ('code', '=', address_dict['state_code']),
                ('country_id', '=', country.id)])
            if states:
                domain += [
                    '|',
                    ('state_id', '=', False),
                    ('state_id', '=', states[0].id)]
        if address_dict.get('zip'):
            domain.append(('zip', '=', address_dict['zip']))
            # sanitize ZIP ?
        partners = rpo.search(domain + [('type', '=', 'delivery')])
        if partners:
            partner = partners[0]
        else:
            partners = rpo.search(domain)
            if partners:
                partner = partners[0]
        return partner

    @api.model
    def _match_product(self, product_dict, chatter_msg, seller=False):
        """Example:
        product_dict = {
            'ean13': '5449000054227',
            'code': 'COCA1L',
            }
        """
        ppo = self.env['product.product']
        self._strip_cleanup_dict(product_dict)
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
            if seller:
                sinfo = self.env['product.supplierinfo'].search([
                    ('name', '=', seller.id),
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
                seller and seller.name or 'None'))

    @api.model
    def _match_currency(self, currency_dict, chatter_msg):
        """Example:
        currency_dict = {
            'iso': 'USD',  # If we have ISO, no need to have more keys
            'symbol': '$',
            'country_code': 'US',
            }
        """
        if not currency_dict:
            currency_dict = {}
        rco = self.env['res.currency']
        self._strip_cleanup_dict(currency_dict)
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
            if len(currencies) == 1:
                return currencies[0]
            else:
                chatter_msg.append(_(
                    "The analysis of the business document returned '%s' as "
                    "the currency symbol. But there are none or several "
                    "currencies with that symbol in Odoo.")
                    % currency_dict['symbol'])
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
            country_code = currency_dict['country_code']
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
        """Example:
        uom_dict = {
            'unece_code': 'LTR',
            'name': 'Liter',
            }
        """
        puo = self.env['product.uom']
        if not uom_dict:
            uom_dict = {}
        self._strip_cleanup_dict(uom_dict)
        if uom_dict.get('recordset'):
            return uom_dict['recordset']
        if uom_dict.get('id'):
            return puo.browse(uom_dict['id'])
        if uom_dict.get('unece_code'):
            # Map NIU to Unit
            if uom_dict['unece_code'] == 'NIU':
                uom_dict['unece_code'] = 'C62'
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
        self._strip_cleanup_dict(tax_dict)
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

    def compare_lines(
            self, existing_lines, import_lines, chatter_msg,
            qty_precision=None, price_precision=None, seller=False):
        """ Example:
        existing_lines = [{
            'product': odoo_recordset,
            'name': 'USB Adapter',
            'qty': 1.5,
            'price_unit': 23.43,  # without taxes
            'uom': uom,
            'line': recordset,
            # Add taxes
            }]
        import_lines = [{
            'product': {
                'ean13': '2100002000003',
                'code': 'EAZY1',
                },
            'quantity': 2,
            'price_unit': 12.42,  # without taxes
            'uom': {'unece_code': 'C62'},
            }]

        Result of the method:
        {
            'to_remove': line_multirecordset,
            'to_add': [
                {'product': recordset1, 'uom', recordset, 'import_line': {import dict},
                # We provide product and uom as recordset to avoid the
                # need to compute a second match
                ]
            'to_update': {
                'line1_recordset': {'qty': [1, 2], 'price_unit': [4.5, 4.6]},
                # qty must be updated from 1 to 2 ; price must be updated from 4.5 to 4.6
                'line2_recordset': {'qty': [12, 13]},  # only qty must be updated
                }
        }

        The check existing_currency == import_currency must be done before
        the call to compare_lines()
        """
        dpo = self.env['decimal.precision']
        if qty_precision is None:
            qty_precision = dpo.precision_get('Product Unit of Measure')
        if price_precision is None:
            price_precision = dpo.precision_get('Product Price')
        existing_lines_dict = {}
        for eline in existing_lines:
            if not eline.get('product'):
                chatter.append(_(
                    "The existing line '%s' doesn't have any product, "
                    "so <b>the lines haven't been updated</b>.")
                    % eline.get('name'))
                return False
            if eline['product'] in existing_lines_dict:
                chatter.append(_(
                    "The product '%s' is used on several existing "
                    "lines, so <b>the lines haven't been updated</b>.")
                    % eline['product'].name_get()[0][1])
                return False
            existing_lines_dict[eline['product']] = eline
        unique_import_products = []
        res = {
            'to_remove': False,
            'to_add': [],
            'to_update': {},
            }
        for iline in import_lines:
            if not iline.get('product'):
                chatter.append(_(
                    "One of the imported lines doesn't have any product, "
                    "so <b>the lines haven't been updated</b>."))
                return False
            product = self._match_product(
                iline['product'], chatter_msg, seller=seller)
            uom = self._match_uom(iline.get('uom'), chatter_msg, product)
            if product in unique_import_products:
                chatter.append(_(
                    "The product '%s' is used on several imported lines, "
                    "so <b>the lines haven't been updated</b>.")
                    % product.name_get()[0][1])
                return False
            unique_import_products.append(product)
            if product in existing_lines_dict:
                if uom != existing_lines_dict[product]['uom']:
                    chatter.append(_(
                        "For product '%s', the unit of measure is %s on the "
                        "existing line, but it is %s on the imported line. "
                        "We don't support this scenario for the moment, so "
                        "<b>the lines haven't been updated</b>.") % (
                            product.name_get()[0][1],
                            existing_lines_dict[product]['uom'].name,
                            uom.name,
                            ))
                    return False
                existing_lines_dict[product]['import'] = True  # used for to_remove
                oline = existing_lines_dict[product]['line']
                res['to_update'][oline] = {}
                if float_compare(
                        iline['qty'],
                        existing_lines_dict[product]['qty'],
                        precision_digits=qty_precision):
                    res['to_update'][oline]['qty'] = [
                        existing_lines_dict[product]['qty'],
                        iline['qty']]
                if (
                        'price_unit' in iline and
                        float_compare(
                            iline['price_unit'],
                            existing_lines_dict[product]['price_unit'],
                            precision_digits=price_precision)):
                    res['to_update'][oline]['price_unit'] = [
                        existing_lines_dict[product]['price_unit'],
                        iline['price_unit']]
            else:
                res['to_add'].append({
                    'product': product,
                    'uom': uom,
                    'import_line': iline,
                    })
        for exiting_dict in existing_lines_dict.itervalues():
            if not exiting_dict.get('import'):
                if res['to_remove']:
                    res['to_remove'] += exiting_dict['line']
                else:
                    res['to_remove'] = exiting_dict['line']
        return res

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

    @api.model
    def post_create_or_update(self, parsed_dict, record):
        if parsed_dict.get('attachments'):
            for filename, data_base64 in\
                    parsed_dict['attachments'].iteritems():
                self.env['ir.attachment'].create({
                    'name': filename,
                    'res_id': record.id,
                    'res_model': unicode(record._model),
                    'datas': data_base64,
                    'datas_fname': filename,
                    })
        for msg in parsed_dict['chatter_msg']:
            record.message_post(msg)
        if parsed_dict.get('note'):
            record.message_post(_(
                '<b>Notes in file %s:</b> %s')
                % (filename, parsed_dict['note']))
