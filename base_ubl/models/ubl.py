# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, tools, _
from openerp.exceptions import Warning as UserError
from lxml import etree
from StringIO import StringIO
from tempfile import NamedTemporaryFile
from PyPDF2 import PdfFileWriter, PdfFileReader
import logging

logger = logging.getLogger(__name__)


class BaseUbl(models.AbstractModel):
    _name = 'base.ubl'
    _description = 'Common methods to generate and parse UBL XML files'

    # ==================== METHODS TO GENERATE UBL files

    @api.model
    def _ubl_add_address(self, partner, node_label, parent_node, ns):
        address = etree.SubElement(parent_node, ns['cac'] + node_label)
        if partner.street:
            street1 = etree.SubElement(address, ns['cbc'] + 'StreetName')
            street1.text = partner.street
            if partner.street2:
                street2 = etree.SubElement(
                    address, ns['cbc'] + 'AdditionalStreetName')
                street2.text = partner.street2
            if hasattr(partner, 'street3') and partner.street3:
                # TODO: see if we have a better tag for street3
                # Check AddressLine/Line
                street3 = etree.SubElement(
                    address, ns['cbc'] + 'BuildingName')
                street3.text = partner.street3
        if partner.city:
            city = etree.SubElement(address, ns['cbc'] + 'CityName')
            city.text = partner.city
        if partner.zip:
            zip = etree.SubElement(address, ns['cbc'] + 'PostalZone')
            zip.text = partner.zip
        if partner.state_id:
            state = etree.SubElement(
                address, ns['cbc'] + 'CountrySubentity')
            state.text = partner.state_id.name
        if partner.country_id:
            country = etree.SubElement(address, ns['cac'] + 'Country')
            country_code = etree.SubElement(
                country, ns['cbc'] + 'IdentificationCode')
            country_code.text = partner.country_id.code
        else:
            logger.warning('UBL: missing country on partner %s', partner.name)

    @api.model
    def _ubl_add_contact(self, partner, parent_node, ns):
        contact = etree.SubElement(parent_node, ns['cac'] + 'Contact')
        if partner.parent_id:
            contact_name = etree.SubElement(contact, ns['cbc'] + 'Name')
            contact_name.text = partner.name
        phone = partner.phone or partner.commercial_partner_id.phone
        if phone:
            telephone = etree.SubElement(contact, ns['cbc'] + 'Telephone')
            telephone.text = phone
        fax = partner.fax or partner.commercial_partner_id.fax
        if fax:
            telefax = etree.SubElement(contact, ns['cbc'] + 'Telefax')
            telefax.text = fax
        email = partner.email or partner.commercial_partner_id.email
        if email:
            electronicmail = etree.SubElement(
                contact, ns['cbc'] + 'ElectronicMail')
            electronicmail.text = email

    @api.model
    def _ubl_add_party(self, partner, parent_node, ns):
        party = etree.SubElement(parent_node, ns['cac'] + 'Party')
        party_name = etree.SubElement(party, ns['cac'] + 'PartyName')
        name = etree.SubElement(party_name, ns['cbc'] + 'Name')
        commercial_partner = partner.commercial_partner_id
        name.text = commercial_partner.name
        self._ubl_add_address(commercial_partner, 'PostalAddress', party, ns)
        if commercial_partner.vat:
            party_tax_scheme = etree.SubElement(
                party, ns['cac'] + 'PartyTaxScheme')
            registration_name = etree.SubElement(
                party_tax_scheme, ns['cbc'] + 'RegistrationName')
            registration_name.text = commercial_partner.name
            company_id = etree.SubElement(
                party_tax_scheme, ns['cbc'] + 'CompanyID')
            company_id.text = commercial_partner.vat
            tax_scheme = etree.SubElement(
                party_tax_scheme, ns['cac'] + 'TaxScheme')
            tax_scheme_id = etree.SubElement(
                tax_scheme, ns['cbc'] + 'ID', schemeID='UN/ECE 5153',
                schemeAgencyID='6')
            tax_scheme_id.text = 'VAT'
        self._ubl_add_contact(partner, party, ns)

    @api.model
    def _ubl_add_product_item(
            self, product, parent_node, ns, type='purchase', seller=False):
        assert type in ('sale', 'purchase'), 'Wrong type param'
        item = etree.SubElement(parent_node, ns['cac'] + 'Item')
        product_name = False
        seller_code = False
        if type == 'purchase':
            descr = product.description_purchase
            if seller:
                sellers = self.env['product.supplierinfo'].search([
                    ('name', '=', seller.id),
                    ('product_tmpl_id', '=', product.product_tmpl_id.id)])
                if sellers:
                    product_name = sellers[0].product_name
                    seller_code = sellers[0].product_code
        elif type == 'sale':
            descr = product.sale_purchase
        if not seller_code:
            seller_code = product.default_code
        if not product_name:
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            product_name = variant and "%s (%s)" % (product.name, variant)\
                or product.name
        if descr:
            description = etree.SubElement(item, ns['cbc'] + 'Description')
            description.text = descr
        name = etree.SubElement(item, ns['cbc'] + 'Name')
        name.text = product_name
        if seller_code:
            seller_identification = etree.SubElement(
                item, ns['cac'] + 'SellersItemIdentification')
            seller_identification_id = etree.SubElement(
                seller_identification, ns['cbc'] + 'ID')
            seller_identification_id.text = seller_code
        if product.ean13:
            std_identification = etree.SubElement(
                item, ns['cac'] + 'StandardItemIdentification')
            std_identification_id = etree.SubElement(
                std_identification, ns['cbc'] + 'ID',
                schemeAgencyID='6', schemeID='GTIN')
            std_identification_id.text = product.ean13
        for attribute_value in product.attribute_value_ids:
            item_property = etree.SubElement(
                item, ns['cac'] + 'AdditionalItemProperty')
            property_name = etree.SubElement(
                item_property, ns['cbc'] + 'Name')
            property_name.text = attribute_value.attribute_id.name
            property_value = etree.SubElement(
                item_property, ns['cbc'] + 'Value')
            property_value.text = attribute_value.name

    @api.model
    def _check_xml_schema(self, xml_string, xsd_file):
        '''Validate the XML file against the XSD'''
        xsd_etree_obj = etree.parse(tools.file_open(xsd_file))
        official_schema = etree.XMLSchema(xsd_etree_obj)
        try:
            t = etree.parse(StringIO(xml_string))
            official_schema.assertValid(t)
        except Exception, e:
            # if the validation of the XSD fails, we arrive here
            logger = logging.getLogger(__name__)
            logger.warning(
                "The XML file is invalid against the XML Schema Definition")
            logger.warning(xml_string)
            logger.warning(e)
            raise UserError(
                _("The generated XML file is not valid against the official "
                    "XML Schema Definition. The generated XML file and the "
                    "full error have been written in the server logs. "
                    "Here is the error, which may give you an idea on the "
                    "cause of the problem : %s.")
                % unicode(e))
        return True

    @api.model
    def embed_xml_in_pdf(self, xml_string, xml_filename, pdf_content):
        logger.debug('Starting to embed %s in PDF file', xml_filename)
        original_pdf_file = StringIO(pdf_content)
        original_pdf = PdfFileReader(original_pdf_file)
        new_pdf_filestream = PdfFileWriter()
        new_pdf_filestream.appendPagesFromReader(original_pdf)
        new_pdf_filestream.addAttachment(xml_filename, xml_string)
        with NamedTemporaryFile(prefix='odoo-ubl-', suffix='.pdf') as f:
            new_pdf_filestream.write(f)
            f.seek(0)
            new_pdf_content = f.read()
            f.close()
            logger.info('%s file added to PDF', xml_filename)
        return new_pdf_content

    # ==================== METHODS TO PARSE UBL files

    @api.model
    def ubl_parse_party(self, party_node, ns):
        partner_name_xpath = party_node.xpath(
            'cac:PartyName/cbc:Name', namespaces=ns)
        vat_xpath = party_node.xpath(
            'cac:PartyTaxScheme/cbc:CompanyID', namespaces=ns)
        email_xpath = party_node.xpath(
            'cac:Contact/cbc:ElectronicMail', namespaces=ns)
        country_code_xpath = party_node.xpath(
            'cac:PostalAddress/cac:Country/cbc:IdentificationCode',
            namespaces=ns)
        country_code = country_code_xpath and country_code_xpath[0].text and\
            country_code_xpath[0].text.upper() or False
        partner_dict = {
            'vat': vat_xpath and vat_xpath[0].text or False,
            'name': partner_name_xpath[0].text,
            'email': email_xpath and email_xpath[0].text or False,
            'country_code': country_code,
            }
        return partner_dict

    def ubl_parse_product(self, line_node, ns):
        ean13_xpath = line_node.xpath(
            "cac:Item/cac:StandardItemIdentification/cbc:ID[@schemeID='GTIN']",
            namespaces=ns)
        code_xpath = line_node.xpath(
            "cac:Item/cac:SellersItemIdentification/cbc:ID", namespaces=ns)
        product_dict = {
            'ean13': ean13_xpath and ean13_xpath[0].text or False,
            'code': code_xpath and code_xpath[0].text or False,
            }
        return product_dict
