# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, tools, _
from openerp.exceptions import Warning as UserError
from openerp.tools import float_compare, float_is_zero
from StringIO import StringIO
from lxml import etree
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from PyPDF2 import PdfFileWriter, PdfFileReader
from tempfile import NamedTemporaryFile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _add_address_block(self, partner, parent_node, ns):
        address = etree.SubElement(
            parent_node, ns['ram'] + 'PostalTradeAddress')
        if partner.zip:
            address_zip = etree.SubElement(
                address, ns['ram'] + 'PostcodeCode')
            address_zip.text = partner.zip
        if partner.street:
            address_street = etree.SubElement(
                address, ns['ram'] + 'LineOne')
            address_street.text = partner.street
            if partner.street2:
                address_street2 = etree.SubElement(
                    address, ns['ram'] + 'LineTwo')
                address_street2.text = partner.street2
        if partner.city:
            address_city = etree.SubElement(
                address, ns['ram'] + 'CityName')
            address_city.text = partner.city
        if partner.country_id:
            address_country = etree.SubElement(
                address, ns['ram'] + 'CountryID')
            address_country.text = partner.country_id.code

    @api.model
    def _add_trade_contact_block(self, partner, parent_node, ns):
        trade_contact = etree.SubElement(
            parent_node, ns['ram'] + 'DefinedTradeContact')
        contact_name = etree.SubElement(
            trade_contact, ns['ram'] + 'PersonName')
        contact_name.text = partner.name
        if partner.phone:
            phone_node = etree.SubElement(
                trade_contact, ns['ram'] + 'TelephoneUniversalCommunication')
            phone_number = etree.SubElement(
                phone_node, ns['ram'] + 'CompleteNumber')
            phone_number.text = partner.phone
        if partner.email:
            email_node = etree.SubElement(
                trade_contact, ns['ram'] + 'EmailURIUniversalCommunication')
            email_uriid = etree.SubElement(
                email_node, ns['ram'] + 'URIID')
            email_uriid.text = partner.email

    @api.model
    def _add_date(self, node_name, date_datetime, parent_node, ns):
        date_node = etree.SubElement(parent_node, ns['ram'] + node_name)
        date_node_str = etree.SubElement(
            date_node, ns['udt'] + 'DateTimeString', format='102')
        # 102 = format YYYYMMDD
        date_node_str.text = date_datetime.strftime('%Y%m%d')

    @api.multi
    def _add_document_context_block(self, root, nsmap, ns):
        self.ensure_one()
        doc_ctx = etree.SubElement(
            root, ns['rsm'] + 'SpecifiedExchangedDocumentContext')
        if self.state not in ('open', 'paid'):
            test_indic = etree.SubElement(doc_ctx, ns['ram'] + 'TestIndicator')
            indic = etree.SubElement(test_indic, ns['udt'] + 'Indicator')
            indic.text = 'true'
        ctx_param = etree.SubElement(
            doc_ctx, ns['ram'] + 'GuidelineSpecifiedDocumentContextParameter')
        ctx_param_id = etree.SubElement(ctx_param, ns['ram'] + 'ID')
        ctx_param_id.text = nsmap['rsm'] + ':comfort'

    @api.multi
    def _add_header_block(self, root, ns):
        self.ensure_one()
        header_doc = etree.SubElement(
            root, ns['rsm'] + 'HeaderExchangedDocument')
        header_doc_id = etree.SubElement(header_doc, ns['ram'] + 'ID')
        if self.state in ('open', 'paid'):
            header_doc_id.text = self.number
        else:
            header_doc_id.text = self.state
        header_doc_name = etree.SubElement(header_doc, ns['ram'] + 'Name')
        if self.type == 'out_refund':
            header_doc_name.text = _('Refund')
        else:
            header_doc_name.text = _('Invoice')
        header_doc_typecode = etree.SubElement(
            header_doc, ns['ram'] + 'TypeCode')
        header_doc_typecode.text = '380'
        # 380 = Commercial invoices (including refund)
        date_invoice_dt = fields.Date.from_string(
            self.date_invoice or fields.Date.context_today(self))
        self._add_date('IssueDateTime', date_invoice_dt, header_doc, ns)
        if self.comment:
            note = etree.SubElement(header_doc, ns['ram'] + 'IncludedNote')
            content_note = etree.SubElement(note, ns['ram'] + 'Content')
            content_note.text = self.comment

    @api.multi
    def _add_trade_agreement_block(self, trade_transaction, ns):
        self.ensure_one()
        trade_agreement = etree.SubElement(
            trade_transaction,
            ns['ram'] + 'ApplicableSupplyChainTradeAgreement')
        company = self.company_id
        seller = etree.SubElement(
            trade_agreement, ns['ram'] + 'SellerTradeParty')
        seller_name = etree.SubElement(
            seller, ns['ram'] + 'Name')
        seller_name.text = company.name
        self._add_trade_contact_block(
            self.user_id.partner_id or company.partner_id, seller, ns)
        self._add_address_block(company.partner_id, seller, ns)
        if company.vat:
            seller_tax_reg = etree.SubElement(
                seller, ns['ram'] + 'SpecifiedTaxRegistration')
            seller_tax_reg_id = etree.SubElement(
                seller_tax_reg, ns['ram'] + 'ID', schemeID='VA')
            seller_tax_reg_id.text = company.vat
        buyer = etree.SubElement(
            trade_agreement, ns['ram'] + 'BuyerTradeParty')
        if self.commercial_partner_id.ref:
            buyer_id = etree.SubElement(
                buyer, ns['ram'] + 'ID')
            buyer_id.text = self.commercial_partner_id.ref
        buyer_name = etree.SubElement(
            buyer, ns['ram'] + 'Name')
        buyer_name.text = self.commercial_partner_id.name
        if self.commercial_partner_id != self.partner_id:
            self._add_trade_contact_block(
                self.partner_id, buyer, ns)
        self._add_address_block(self.partner_id, buyer, ns)
        if self.commercial_partner_id.vat:
            buyer_tax_reg = etree.SubElement(
                buyer, ns['ram'] + 'SpecifiedTaxRegistration')
            buyer_tax_reg_id = etree.SubElement(
                buyer_tax_reg, ns['ram'] + 'ID', schemeID='VA')
            buyer_tax_reg_id.text = self.commercial_partner_id.vat

    @api.multi
    def _add_trade_settlement_payment_means_block(
            self, trade_settlement, sign, ns):
        payment_means = etree.SubElement(
            trade_settlement,
            ns['ram'] + 'SpecifiedTradeSettlementPaymentMeans')
        payment_means_code = etree.SubElement(
            payment_means, ns['ram'] + 'TypeCode')
        payment_means_info = etree.SubElement(
            payment_means, ns['ram'] + 'Information')
        if self.payment_mode_id:
            payment_means_code.text = self.payment_mode_id.type.zugferd_code
            payment_means_info.text =\
                self.payment_mode_id.note or self.payment_mode_id.name
        else:
            payment_means_code.text = '31'  # 31 = Wire transfer
            payment_means_info.text = _('Wire transfer')
            logger.warning(
                'Missing payment mode on invoice ID %d. '
                'Using 31 (wire transfer) as zugferd code as fallback '
                'for payment mean',
                self.id)
        if payment_means_code.text in ['31', '42']:
            partner_bank = self.partner_bank_id
            if not partner_bank and self.payment_mode_id:
                partner_bank = self.payment_mode_id.bank_id
            if partner_bank and partner_bank.state == 'iban':
                payment_means_bank_account = etree.SubElement(
                    payment_means,
                    ns['ram'] + 'PayeePartyCreditorFinancialAccount')
                iban = etree.SubElement(
                    payment_means_bank_account, ns['ram'] + 'IBANID')
                iban.text = partner_bank.acc_number.replace(' ', '')
                if partner_bank.bank_bic:
                    payment_means_bank = etree.SubElement(
                        payment_means,
                        ns['ram'] +
                        'PayeeSpecifiedCreditorFinancialInstitution')
                    payment_means_bic = etree.SubElement(
                        payment_means_bank, ns['ram'] + 'BICID')
                    payment_means_bic.text = partner_bank.bank_bic
                    if partner_bank.bank_name:
                        bank_name = etree.SubElement(
                            payment_means_bank, ns['ram'] + 'Name')
                        bank_name.text = partner_bank.bank_name

    @api.multi
    def _add_trade_settlement_block(self, trade_transaction, sign, ns):
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get('Account')
        inv_currency_name = self.currency_id.name
        trade_settlement = etree.SubElement(
            trade_transaction,
            ns['ram'] + 'ApplicableSupplyChainTradeSettlement')
        payment_ref = etree.SubElement(
            trade_settlement, ns['ram'] + 'PaymentReference')
        payment_ref.text = self.number or self.state
        invoice_currency = etree.SubElement(
            trade_settlement, ns['ram'] + 'InvoiceCurrencyCode')
        invoice_currency.text = inv_currency_name
        if (
                self.payment_mode_id and
                not self.payment_mode_id.type.zugferd_code):
            raise UserError(_(
                "Missing ZUGFeRD code on payment export type '%s'")
                % self.payment_mode_id.type.name)
        if (
                self.type == 'out_invoice' or
                (self.payment_mode_id and
                 self.payment_mode_id.type.zugferd_code not in [31, 42])):
            self._add_trade_settlement_payment_means_block(
                trade_settlement, sign, ns)
        tax_basis_total = 0.0
        if self.tax_line:
            for tline in self.tax_line:
                if not tline.base_code_id:
                    raise UserError(_(
                        "Missing base code on tax line '%s'.") % tline.name)
                taxes = self.env['account.tax'].search([
                    ('base_code_id', '=', tline.base_code_id.id)])
                if not taxes:
                    raise UserError(_(
                        "The tax code '%s' is not linked to a tax.")
                        % tline.base_code_id.name)
                tax = taxes[0]
                if not tax.zugferd_type_code:
                    raise UserError(_(
                        "Missing ZUGFeRD Type Code on tax '%s'") % tax.name)
                if not tax.zugferd_categ_code:
                    raise UserError(_(
                        "Missing ZUGFeRD Category Code on tax '%s'")
                        % tax.name)
                trade_tax = etree.SubElement(
                    trade_settlement, ns['ram'] + 'ApplicableTradeTax')
                amount = etree.SubElement(
                    trade_tax, ns['ram'] + 'CalculatedAmount',
                    currencyID=inv_currency_name)
                amount.text = unicode(tline.amount * sign)
                tax_type = etree.SubElement(
                    trade_tax, ns['ram'] + 'TypeCode')
                tax_type.text = tax.zugferd_type_code

                if (
                        tax.zugferd_categ_code != 'S' and
                        float_is_zero(tax.amount, precision_digits=prec) and
                        self.fiscal_position and
                        self.fiscal_position.note):
                    exemption_reason = etree.SubElement(
                        trade_tax, ns['ram'] + 'ExemptionReason')
                    exemption_reason.text = self.with_context(
                        lang=self.partner_id.lang or 'en_US').\
                        fiscal_position.note

                base = etree.SubElement(
                    trade_tax,
                    ns['ram'] + 'BasisAmount', currencyID=inv_currency_name)
                base.text = unicode(tline.base * sign)
                tax_basis_total += tline.base
                tax_categ_code = etree.SubElement(
                    trade_tax, ns['ram'] + 'CategoryCode')
                tax_categ_code.text = tax.zugferd_categ_code
                if tax.type == 'percent':
                    percent = etree.SubElement(
                        trade_tax, ns['ram'] + 'ApplicablePercent')
                    percent.text = unicode(tax.amount * 100)
        trade_payment_term = etree.SubElement(
            trade_settlement, ns['ram'] + 'SpecifiedTradePaymentTerms')
        if self.payment_term:
            trade_payment_term_desc = etree.SubElement(
                trade_payment_term, ns['ram'] + 'Description')
            trade_payment_term_desc.text = self.payment_term.name

        date_due_dt = fields.Date.from_string(self.date_due)
        self._add_date(
            'DueDateDateTime', date_due_dt, trade_payment_term, ns)

        sums = etree.SubElement(
            trade_settlement,
            ns['ram'] + 'SpecifiedTradeSettlementMonetarySummation')
        line_total = etree.SubElement(
            sums, ns['ram'] + 'LineTotalAmount', currencyID=inv_currency_name)
        line_total.text = unicode(self.amount_untaxed * sign)
        charge_total = etree.SubElement(
            sums, ns['ram'] + 'ChargeTotalAmount',
            currencyID=inv_currency_name)
        charge_total.text = '0.00'
        allowance_total = etree.SubElement(
            sums, ns['ram'] + 'AllowanceTotalAmount',
            currencyID=inv_currency_name)
        allowance_total.text = '0.00'
        tax_basis_total_amt = etree.SubElement(
            sums, ns['ram'] + 'TaxBasisTotalAmount',
            currencyID=inv_currency_name)
        tax_basis_total_amt.text = unicode(tax_basis_total * sign)
        tax_total = etree.SubElement(
            sums, ns['ram'] + 'TaxTotalAmount', currencyID=inv_currency_name)
        tax_total.text = unicode(self.amount_tax * sign)
        total = etree.SubElement(
            sums, ns['ram'] + 'GrandTotalAmount', currencyID=inv_currency_name)
        total.text = unicode(self.amount_total * sign)
        prepaid = etree.SubElement(
            sums, ns['ram'] + 'TotalPrepaidAmount',
            currencyID=inv_currency_name)
        residual = etree.SubElement(
            sums, ns['ram'] + 'DuePayableAmount', currencyID=inv_currency_name)
        prepaid.text = unicode((self.amount_total - self.residual) * sign)
        residual.text = unicode(self.residual * sign)

    @api.multi
    def _add_invoice_line_block(self, trade_transaction, iline, sign, ns):
        self.ensure_one()
        pp_prec = self.env['decimal.precision'].precision_get('Product Price')
        disc_prec = self.env['decimal.precision'].precision_get('Discount')
        inv_currency_name = self.currency_id.name
        line_item = etree.SubElement(
            trade_transaction,
            ns['ram'] + 'IncludedSupplyChainTradeLineItem')
        line_trade_agreement = etree.SubElement(
            line_item,
            ns['ram'] + 'SpecifiedSupplyChainTradeAgreement')
        gross_price_val = iline.price_unit
        net_price_val = iline.price_unit * (
            1 - (iline.discount or 0.0) / 100.0)
        gross_price = etree.SubElement(
            line_trade_agreement,
            ns['ram'] + 'GrossPriceProductTradePrice')
        gross_price_amount = etree.SubElement(
            gross_price, ns['ram'] + 'ChargeAmount',
            currencyID=inv_currency_name)
        gross_price_amount.text = unicode(gross_price_val)
        fc_discount = float_compare(
            iline.discount, 0.0, precision_digits=disc_prec)
        if fc_discount in [-1, 1]:
            trade_allowance = etree.SubElement(
                gross_price, ns['ram'] + 'AppliedTradeAllowanceCharge')
            charge_indic = etree.SubElement(
                trade_allowance, ns['ram'] + 'ChargeIndicator')
            indicator = etree.SubElement(
                charge_indic, ns['udt'] + 'Indicator')
            if fc_discount == 1:
                indicator.text = 'false'
            else:
                indicator.text = 'true'
            actual_amount = etree.SubElement(
                trade_allowance, ns['ram'] + 'ActualAmount',
                currencyID=inv_currency_name)
            actual_amount_val = round(gross_price_val - net_price_val, pp_prec)
            actual_amount.text = unicode(abs(actual_amount_val))

        net_price = etree.SubElement(
            line_trade_agreement, ns['ram'] + 'NetPriceProductTradePrice')
        net_price_amount = etree.SubElement(
            net_price, ns['ram'] + 'ChargeAmount',
            currencyID=inv_currency_name)
        net_price_amount.text = unicode(net_price_val)
        line_trade_delivery = etree.SubElement(
            line_item, ns['ram'] + 'SpecifiedSupplyChainTradeDelivery')
        if iline.uos_id and iline.uos_id.zugferd_code:
            unitCode = iline.uos_id.zugferd_code
        else:
            unitCode = 'C62'
            if not iline.uos_id:
                logger.warning(
                    "No unit of measure on invoice line '%s', "
                    "using C62 (piece) as fallback",
                    iline.name)
            else:
                logger.warning(
                    'Missing zugferd_code on unit of measure %s, '
                    'using C62 (piece) as fallback',
                    iline.uos_id.name)
        billed_qty = etree.SubElement(
            line_trade_delivery, ns['ram'] + 'BilledQuantity',
            unitCode=unitCode)
        billed_qty.text = unicode(iline.quantity * sign)
        line_trade_settlement = etree.SubElement(
            line_item, ns['ram'] + 'SpecifiedSupplyChainTradeSettlement')
        if iline.invoice_line_tax_id:
            for tax in iline.invoice_line_tax_id:
                trade_tax = etree.SubElement(
                    line_trade_settlement,
                    ns['ram'] + 'ApplicableTradeTax')
                trade_tax_typecode = etree.SubElement(
                    trade_tax, ns['ram'] + 'TypeCode')
                if not tax.zugferd_type_code:
                    raise UserError(_(
                        "Missing ZUGFeRD Type Code on tax '%s'")
                        % tax.name)
                trade_tax_typecode.text = tax.zugferd_type_code
                trade_tax_categcode = etree.SubElement(
                    trade_tax, ns['ram'] + 'CategoryCode')
                if not tax.zugferd_categ_code:
                    raise UserError(_(
                        "Missing ZUGFeRD Category Code on tax '%s'")
                        % tax.name)
                trade_tax_categcode.text = tax.zugferd_categ_code
                if tax.type == 'percent':
                    trade_tax_percent = etree.SubElement(
                        trade_tax, ns['ram'] + 'ApplicablePercent')
                    trade_tax_percent.text = unicode(tax.amount * 100)
        subtotal = etree.SubElement(
            line_trade_settlement,
            ns['ram'] + 'SpecifiedTradeSettlementMonetarySummation')
        subtotal_amount = etree.SubElement(
            subtotal, ns['ram'] + 'LineTotalAmount',
            currencyID=inv_currency_name)
        subtotal_amount.text = unicode(iline.price_subtotal * sign)
        trade_product = etree.SubElement(
            line_item, ns['ram'] + 'SpecifiedTradeProduct')
        if iline.product_id:
            if iline.product_id.ean13:
                ean13 = etree.SubElement(
                    trade_product, ns['ram'] + 'GlobalID', schemeID='0160')
                # 0160 = GS1 Global Trade Item Number (GTIN, EAN)
                ean13.text = iline.product_id.ean13
            if iline.product_id.default_code:
                product_code = etree.SubElement(
                    trade_product, ns['ram'] + 'SellerAssignedID')
                product_code.text = iline.product_id.default_code
            if iline.product_id.description_sale:
                product_desc = etree.SubElement(
                    trade_product, ns['ram'] + 'Description')
                product_desc.text = iline.product_id.description_sale
        product_name = etree.SubElement(
            trade_product, ns['ram'] + 'Name')
        product_name.text = iline.name

    @api.multi
    def generate_zugferd_xml(self):
        self.ensure_one()
        assert self.type in ('out_invoice', 'out_refund'),\
            'only works for customer invoice and refunds'
        sign = self.type == 'out_refund' and -1 or 1
        nsmap = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'rsm': 'urn:ferd:CrossIndustryDocument:invoice:1p0',
            'ram': 'urn:un:unece:uncefact:data:standard:'
                   'ReusableAggregateBusinessInformationEntity:12',
            'udt': 'urn:un:unece:uncefact:data:'
                   'standard:UnqualifiedDataType:15',
            }
        ns = {
            'rsm': '{urn:ferd:CrossIndustryDocument:invoice:1p0}',
            'ram': '{urn:un:unece:uncefact:data:standard:'
                   'ReusableAggregateBusinessInformationEntity:12}',
            'udt': '{urn:un:unece:uncefact:data:standard:'
                   'UnqualifiedDataType:15}',
            }

        root = etree.Element(ns['rsm'] + 'CrossIndustryDocument', nsmap=nsmap)

        self._add_document_context_block(root, nsmap, ns)
        self._add_header_block(root, ns)

        trade_transaction = etree.SubElement(
            root, ns['rsm'] + 'SpecifiedSupplyChainTradeTransaction')

        self._add_trade_agreement_block(trade_transaction, ns)
        self._add_trade_settlement_block(trade_transaction, sign, ns)

        for iline in self.invoice_line:
            self._add_invoice_line_block(trade_transaction, iline, sign, ns)

        xml_string = etree.tostring(
            root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        self._check_xml_schema(
            xml_string, 'account_invoice_zugferd/data/ZUGFeRD1p0.xsd')
        logger.debug(
            'ZUGFeRD XML file generated by Odoo for invoice ID %d', self.id)
        logger.debug(xml_string)
        return xml_string

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
    def pdf_is_zugferd(self, pdf_content):
        is_zugferd = False
        try:
            fd = StringIO(pdf_content)
            parser = PDFParser(fd)
            doc = PDFDocument(parser)
            logger.debug('doc.catalog=%s', doc.catalog)
            # The code below will have to be adapted when we get samples
            # of PDF files with embedded XML other than ZUGFeRD
            embeddedfile = doc.catalog['Names']['EmbeddedFiles']['Names']
            if embeddedfile[0] == 'ZUGFeRD-invoice.xml':
                is_zugferd = True
            else:
                is_zugferd = False
        except:
            pass
        logger.debug('pdf_is_zugferd returns %s', is_zugferd)
        return is_zugferd

    @api.multi
    def _prepare_pdf_invoice_metadata(self):
        self.ensure_one()
        now_dt = datetime.now()
        pdf_date = now_dt.strftime("D:%Y%m%d%H%M%S+00'00'")
        # example date format: "D:20141006161354+02'00'"
        metadata = {
            'Author': self.env.user.company_id.name,
            'CreationDate': pdf_date,
            'Creator': 'Odoo module account_invoice_zugferd',
            'Keywords': '',
            'ModDate': pdf_date,
            'Subject': '',
            'Title': 'Invoice %s' % self.number or self.state,
            }
        return metadata

    @api.multi
    def regular_pdf_invoice_to_zugferd_invoice(self, pdf_content):
        """This method is independent from the reporting engine"""
        self.ensure_one()
        if not self.pdf_is_zugferd(pdf_content):
            if self.type in ('out_invoice', 'out_refund'):
                zugferd_xml_str = self.generate_zugferd_xml()
                # Generate a new PDF with XML file as attachment
                original_pdf_file = StringIO(pdf_content)
                original_pdf = PdfFileReader(original_pdf_file)
                new_pdf_filestream = PdfFileWriter()
                new_pdf_filestream.appendPagesFromReader(original_pdf)
                new_pdf_filestream.addAttachment(
                    'ZUGFeRD-invoice.xml', zugferd_xml_str)
                new_pdf_filestream.addMetadata(
                    self._prepare_pdf_invoice_metadata())
                # TODO : add 'AFRelationship': /Alternative
                # and all other metadata required by ZUGFeRD
                # including the extension schema
                prefix = 'odoo-invoice-zugferd-'
                with NamedTemporaryFile(prefix=prefix, suffix='.pdf') as f:
                    new_pdf_filestream.write(f)
                    f.seek(0)
                    pdf_content = f.read()
                    f.close()
                logger.info('ZUGFeRD-invoice.xml file added to PDF invoice')
        return pdf_content
