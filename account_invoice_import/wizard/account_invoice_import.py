# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare, float_round, float_is_zero
from openerp.exceptions import Warning as UserError
from lxml import etree
import logging
import mimetypes

logger = logging.getLogger(__name__)


class AccountInvoiceImport(models.TransientModel):
    _name = 'account.invoice.import'
    _inherit = ['business.document.import']
    _description = 'Wizard to import supplier invoices/refunds'

    invoice_file = fields.Binary(
        string='PDF or XML Invoice', required=True)
    invoice_filename = fields.Char(string='Filename')
    state = fields.Selection([
        ('import', 'Import'),
        ('update', 'Update'),
        ('update-from-invoice', 'Update From Invoice'),
        ], string='State', default="import")
    partner_id = fields.Many2one(
        'res.partner', string="Supplier", readonly=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', readonly=True)
    invoice_type = fields.Selection([
        ('in_invoice', 'Invoice'),
        ('in_refund', 'Refund'),
        ], string="Invoice or Refund", readonly=True)
    amount_untaxed = fields.Float(
        string='Total Untaxed', digits=dp.get_precision('Account'),
        readonly=True)
    amount_total = fields.Float(
        string='Total', digits=dp.get_precision('Account'),
        readonly=True)
    invoice_id = fields.Many2one(
        'account.invoice', string='Draft Supplier Invoice to Update')

    @api.model
    def parse_xml_invoice(self, xml_root):
        raise UserError(_(
            "This type of XML invoice is not supported. Did you install "
            "the module to support this type of file?"))

    @api.model
    def parse_pdf_invoice(self, file_data):
        '''This method must be inherited by additionnal modules with
        the same kind of logic as the account_bank_statement_import_*
        modules'''
        xml_files_dict = self.get_xml_files_from_pdf(file_data)
        for xml_filename, xml_root in xml_files_dict.iteritems():
            logger.info('Trying to parse XML file %s', xml_filename)
            try:
                parsed_inv = self.parse_xml_invoice(xml_root)
                return parsed_inv
            except:
                continue
        parsed_inv = self.fallback_parse_pdf_invoice(file_data)
        if not parsed_inv:
            raise UserError(_(
                "This type of PDF invoice is not supported. Did you install "
                "the module to support this type of file?"))
        return parsed_inv

    def fallback_parse_pdf_invoice(self, file_data):
        '''Designed to be inherited by the module
        account_invoice_import_invoice2data, to be sure the invoice2data
        technique is used after the electronic invoice modules such as
        account_invoice_import_zugferd
        '''
        return False

        # Dict to return:
        # {
        # 'currency': {
        #    'iso': 'EUR',
        #    'currency_symbol': u'€',  # The one or the other
        #    },
        # 'date': '2015-10-08',  # Must be a string
        # 'date_due': '2015-11-07',
        # 'date_start': '2015-10-01',  # for services over a period of time
        # 'date_end': '2015-10-31',
        # 'amount_untaxed': 10.0,  # < 0 for refunds
        # 'amount_tax': 2.0,  # provide amount_untaxed OR amount_tax
        # 'amount_total': 12.0,  # Total with taxes, must always be provided
        # 'partner': {
        #       'vat': 'FR25499247138',
        #       'email': 'support@browserstack.com',
        #       'name': 'Capitaine Train',
        #       },
        # 'partner': res.partner recordset,
        # 'invoice_number': 'I1501243',
        # 'description': 'TGV Paris-Lyon',
        # 'attachments': {'file1.pdf': base64data1, 'file2.pdf': base64data2},
        # 'chatter_msg': ['Notes added in chatter of the invoice'],
        # 'note': 'Note embedded in the document',
        # 'lines': [{
        #       'product': {
        #           'ean13': '4123456000021',
        #           'code': 'GZ250',
        #           },
        #       'name': 'Gelierzucker Extra 250g',
        #       'price_unit': 1.45, # price_unit without taxes always positive
        #       'qty': -2.0,  # < 0 when it's a refund
        #       'uom': {'unece_code': 'C62'},
        #       'taxes': [list of tax_dict],
        #       }],
        # }

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv):
        aio = self.env['account.invoice']
        ailo = self.env['account.invoice.line']
        company = self.env.user.company_id
        assert parsed_inv.get('amount_total'), 'Missing amount_total'
        partner = self._match_partner(
            parsed_inv['partner'], parsed_inv['chatter_msg'])
        partner = partner.commercial_partner_id
        currency = self._match_currency(
            parsed_inv.get('currency'), parsed_inv['chatter_msg'])
        vals = {
            'partner_id': partner.id,
            'currency_id': currency.id,
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
            'in_invoice', partner.id, company_id=company.id)['value'])
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
                parsed_inv['chatter_msg'].append(_(
                    "The bank account <b>IBAN %s</b> has been automatically "
                    "added on the supplier <b>%s</b>") % (
                    parsed_inv['iban'], partner.name))
        config = partner.invoice_import_id
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
                    partner_id=partner.id,
                    fposition_id=partner.property_account_position.id,
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
            self.set_1line_start_end_dates(il_vals, parsed_inv)
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
                    }
            elif config.invoice_line_method == 'nline_static_product':
                sproduct = config.static_product_id
                static_vals = ailo.product_id_change(
                    sproduct.id, sproduct.uom_id.id, type='in_invoice',
                    partner_id=partner.id,
                    fposition_id=partner.property_account_position.id,
                    company_id=company.id)['value']
                static_vals['product_id'] = sproduct.id
            else:
                static_vals = {}
            for line in parsed_inv['lines']:
                il_vals = static_vals.copy()
                if config.invoice_line_method == 'nline_auto_product':
                    product = self._match_product(
                        line['product'], parsed_inv['chatter_msg'],
                        seller=partner)
                    fposition_id = partner.property_account_position.id
                    il_vals.update(
                        ailo.product_id_change(
                            product.id, product.uom_id.id, type='in_invoice',
                            partner_id=partner.id,
                            fposition_id=fposition_id,
                            company_id=company.id)['value'])
                    il_vals['product_id'] = product.id
                elif config.invoice_line_method == 'nline_no_product':
                    taxes = self._match_taxes(
                        line.get('taxes'), parsed_inv['chatter_msg'])
                    il_vals['invoice_line_tax_id'] = taxes.ids
                if line.get('name'):
                    il_vals['name'] = line['name']
                elif not il_vals.get('name'):
                    il_vals['name'] = _('MISSING DESCRIPTION')
                uom = self._match_uom(
                    line.get('uom'), parsed_inv['chatter_msg'])
                il_vals['uos_id'] = uom.id
                il_vals.update({
                    'quantity': line['qty'],
                    'price_unit': line['price_unit'],  # TODO fix for tax incl
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
    def set_1line_start_end_dates(self, il_vals, parsed_inv):
        """Only useful if you have installed the module account_cutoff_prepaid
        from https://github.com/OCA/account-closing"""
        fakeiline = self.env['account.invoice.line'].browse(False)
        if (
                parsed_inv.get('date_start') and
                parsed_inv.get('date_end') and
                hasattr(fakeiline, 'start_date') and
                hasattr(fakeiline, 'end_date')):
            il_vals['start_date'] = parsed_inv.get('date_start')
            il_vals['end_date'] = parsed_inv.get('date_end')

    @api.multi
    def parse_invoice(self):
        self.ensure_one()
        assert self.invoice_file, 'No invoice file'
        logger.info('Starting to import invoice %s', self.invoice_filename)
        file_data = self.invoice_file.decode('base64')
        parsed_inv = {}
        filetype = mimetypes.guess_type(self.invoice_filename)
        logger.debug('Invoice mimetype: %s', filetype)
        if filetype and filetype[0] == 'application/xml':
            try:
                xml_root = etree.fromstring(file_data)
            except:
                raise UserError(_(
                    "This XML file is not XML-compliant"))
            pretty_xml_string = etree.tostring(
                xml_root, pretty_print=True, encoding='UTF-8',
                xml_declaration=True)
            logger.debug('Starting to import the following XML file:')
            logger.debug(pretty_xml_string)
            parsed_inv = self.parse_xml_invoice(xml_root)
        # Fallback on PDF
        else:
            parsed_inv = self.parse_pdf_invoice(file_data)
        if 'attachments' not in parsed_inv:
            parsed_inv['attachments'] = {}
        parsed_inv['attachments'][self.invoice_filename] = self.invoice_file
        updated_parsed_inv = self.update_clean_parsed_inv(parsed_inv)
        return updated_parsed_inv

    @api.model
    def update_clean_parsed_inv(self, parsed_inv):
        prec_ac = self.env['decimal.precision'].precision_get('Account')
        prec_pp = self.env['decimal.precision'].precision_get('Product Price')
        prec_uom = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if 'amount_tax' in parsed_inv and 'amount_untaxed' not in parsed_inv:
            parsed_inv['amount_untaxed'] =\
                parsed_inv['amount_total'] - parsed_inv['amount_tax']
        elif (
                'amount_untaxed' not in parsed_inv and
                'amount_tax' not in parsed_inv):
            # For invoices that never have taxes
            parsed_inv['amount_untaxed'] = parsed_inv['amount_total']
        if float_compare(
                parsed_inv['amount_total'], 0, precision_digits=prec_ac) == -1:
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
                line['qty'] = float_round(
                    line['qty'], precision_digits=prec_uom)
                line['price_unit'] = float_round(
                    line['price_unit'], precision_digits=prec_pp)
                if parsed_inv['type'] == 'in_refund':
                    line['qty'] *= -1
        if 'chatter_msg' not in parsed_inv:
            parsed_inv['chatter_msg'] = []
        logger.debug('Resulf of invoice parsing parsed_inv=%s', parsed_inv)
        return parsed_inv

    @api.multi
    def import_invoice(self):
        """Method called by the button of the wizard (1st step)"""
        self.ensure_one()
        aio = self.env['account.invoice']
        iaao = self.env['ir.actions.act_window']
        parsed_inv = self.parse_invoice()
        partner = self._match_partner(
            parsed_inv['partner'], parsed_inv['chatter_msg'])
        partner = partner.commercial_partner_id
        currency = self._match_currency(
            parsed_inv.get('currency'), parsed_inv['chatter_msg'])
        parsed_inv['partner']['recordset'] = partner
        parsed_inv['currency']['recordset'] = currency
        # TODO Move to IF below : make sure we don't access self.partner_id
        self.write({
            'partner_id': partner.id,
            'invoice_type': parsed_inv['type'],
            'currency_id': currency.id,
            'amount_untaxed': parsed_inv['amount_untaxed'],
            'amount_total': parsed_inv['amount_total'],
            })
        if not partner.invoice_import_id:
            raise UserError(_(
                "Missing Invoice Import Configuration on partner '%s'.")
                % partner.name)
        domain = [
            ('commercial_partner_id', '=', partner.id),
            ('type', '=', parsed_inv['type'])]
        existing_invs = aio.search(
            domain +
            [(
                'supplier_invoice_number',
                '=ilike',
                parsed_inv.get('invoice_number'))])
        if existing_invs:
            raise UserError(_(
                "This invoice already exists in Odoo. It's "
                "Supplier Invoice Number is '%s' and it's Odoo number "
                "is '%s'")
                % (parsed_inv.get('invoice_number'), existing_invs[0].number))
        draft_same_supplier_invs = aio.search(
            domain + [('state', '=', 'draft')])
        logger.debug('draft_same_supplier_invs=%s', draft_same_supplier_invs)
        if draft_same_supplier_invs:
            action = iaao.for_xml_id(
                'account_invoice_import',
                'account_invoice_import_action')
            default_invoice_id = False
            if len(draft_same_supplier_invs) == 1:
                default_invoice_id = draft_same_supplier_invs[0].id
            self.write({
                'state': 'update',
                'invoice_id': default_invoice_id,
            })
            action['res_id'] = self.id
            return action
        else:
            action = self.create_invoice()
            return action

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        iaao = self.env['ir.actions.act_window']
        parsed_inv = self.parse_invoice()
        invoice = self._create_invoice(parsed_inv)
        invoice.message_post(_(
            "This invoice has been created automatically via file import"))
        action = iaao.for_xml_id('account', 'action_invoice_tree2')
        action.update({
            'view_mode': 'form,tree,calendar,graph',
            'views': False,
            'res_id': invoice.id,
            })
        return action

    @api.model
    def _create_invoice(self, parsed_inv):
        aio = self.env['account.invoice']
        vals = self._prepare_create_invoice_vals(parsed_inv)
        logger.debug('Invoice vals for creation: %s', vals)
        invoice = aio.create(vals)
        self.post_process_invoice(parsed_inv, invoice)
        logger.info('Invoice ID %d created', invoice.id)
        self.post_create_or_update(parsed_inv, invoice)
        return invoice

    @api.model
    def post_process_invoice(self, parsed_inv, invoice):
        self.ensure_one()
        invoice = self[0]
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
            if not invoice.tax_line:
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

    @api.multi
    def update_invoice_lines(self, parsed_inv, invoice, seller):
        chatter = parsed_inv['chatter_msg']
        ailo = self.env['account.invoice.line']
        dpo = self.env['decimal.precision']
        qty_prec = dpo.precision_get('Product Unit of Measure')
        existing_lines = []
        for eline in invoice.invoice_line:
            price_unit = 0.0
            if not float_is_zero(
                    eline.quantity, precision_digits=qty_prec):
                price_unit = eline.price_subtotal / float(eline.quantity)
            existing_lines.append({
                'product': eline.product_id or False,
                'name': eline.name,
                'qty': eline.quantity,
                'uom': eline.uos_id,
                'line': eline,
                'price_unit': price_unit,
                })
        compare_res = self.compare_lines(
            existing_lines, parsed_inv['lines'], chatter, seller=seller)
        for eline, cdict in compare_res['to_update'].iteritems():
            write_vals = {}
            if cdict.get('qty'):
                chatter.append(_(
                    "The quantity has been updated on the invoice line "
                    "with product '%s' from %s to %s %s") % (
                        eline.product_id.name_get()[0][1],
                        cdict['qty'][0], cdict['qty'][1],
                        eline.uos_id.name))
                write_vals['quantity'] = cdict['qty'][1]
            if cdict.get('price_unit'):
                chatter.append(_(
                    "The unit price has been updated on the invoice "
                    "line with product '%s' from %s to %s %s") % (
                        eline.product_id.name_get()[0][1],
                        eline.price_unit, cdict['price_unit'][1],  # TODO fix
                        invoice.currency_id.name))
                write_vals['price_unit'] = cdict['price_unit'][1]
            if write_vals:
                eline.write(write_vals)
        if compare_res['to_remove']:
            to_remove_label = [
                '%s %s x %s' % (
                    l.quantity, l.uos_id.name, l.product_id.name)
                for l in compare_res['to_remove']]
            chatter.append(_(
                "%d invoice line(s) deleted: %s") % (
                    len(compare_res['to_remove']),
                    ', '.join(to_remove_label)))
            compare_res['to_remove'].unlink()
        if compare_res['to_add']:
            to_create_label = []
            for add in compare_res['to_add']:
                line_vals = self._prepare_create_invoice_line(
                    add['product'], add['uom'], add['import_line'])
                line_vals['invoice_id'] = invoice.id
                new_line = ailo.create(line_vals)
                to_create_label.append('%s %s x %s' % (
                    new_line.quantity,
                    new_line.uos_id.name,
                    new_line.name))
            chatter.append(_("%d new invoice line(s) created: %s") % (
                len(compare_res['to_add']), ', '.join(to_create_label)))
        return True

    @api.model
    def _prepare_create_order_line(self, product, uom, import_line, invoice):
        ailo = self.env['account.invoice.line']
        vals = ailo.product_id_change(
            product.id, uom.id, qty=import_line['qty'], type='in_invoice',
            partner_id=invoice.partner_id.id,
            fposition_id=invoice.fiscal_position.id or False,
            currency_id=invoice.currency_id.id,
            company_id=invoice.company_id.id)['value']
        vals.update({
            'product_id': product.id,
            'price_unit': import_line.get('price_unit'),
            'quantity': import_line['qty'],
            })
        return vals

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
        invoice = self.invoice_id
        if not invoice:
            raise UserError(_(
                'You must select a supplier invoice or refund to update'))
        parsed_inv = self.parse_invoice()
        if self.partner_id:
            # True if state='update' ; False when state='update-from-invoice'
            parsed_inv['partner']['recordset'] = self.partner_id
        partner = self._match_partner(
            parsed_inv['partner'], parsed_inv['chatter_msg'],
            partner_type='supplier')
        partner = partner.commercial_partner_id
        if partner != invoice.commercial_partner_id:
            raise UserError(_(
                "The supplier of the imported invoice (%s) is different from "
                "the supplier of the invoice to update (%s).") % (
                    partner.name,
                    invoice.commercial_partner_id.name))
        if not partner.invoice_import_id:
            raise UserError(_(
                "Missing Invoice Import Configuration on partner '%s'.")
                % partner.name)
        currency = self._match_currency(
            parsed_inv.get('currency'), parsed_inv['chatter_msg'])
        if currency != invoice.currency_id:
            raise UserError(_(
                "The currency of the imported invoice (%s) is different from "
                "the currency of the existing invoice (%s)") % (
                currency.name, invoice.currency_id.name))
        # When invoice with embedded XML files will be more widely used,
        # we should also update invoice lines
        vals = self._prepare_update_invoice_vals(parsed_inv)
        logger.debug('Updating supplier invoice with vals=%s', vals)
        self.invoice_id.write(vals)
        if (
                parsed_inv.get('lines') and
                partner.invoice_import_id.invoice_line_method ==
                'nline_auto_product'):
            self.update_invoice_lines(parsed_inv, invoice, partner)
        self.post_process_invoice(parsed_inv, invoice)
        if partner.invoice_import_id.account_analytic_id:
            invoice.invoice_line.write({
                'account_analytic_id':
                partner.invoice_import_id.account_analytic_id.id})
        self.post_create_or_update(parsed_inv, invoice)
        logger.info(
            'Supplier invoice ID %d updated via import of file %s',
            invoice.id, self.invoice_filename)
        invoice.message_post(_(
            "This invoice has been updated automatically via the import "
            "of file %s") % self.invoice_filename)
        action = iaao.for_xml_id('account', 'action_invoice_tree2')
        action.update({
            'view_mode': 'form,tree,calendar,graph',
            'views': False,
            'res_id': invoice.id,
            })
        return action
