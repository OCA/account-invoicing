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
from openerp.tools import float_compare
from openerp.exceptions import Warning as UserError
from datetime import datetime
import logging
import os
import base64
from tempfile import mkstemp
from invoice2data.main import extract_data

logger = logging.getLogger(__name__)


class AccountInvoicePdfImport(models.TransientModel):
    _name = 'account.invoice.pdf.import'
    _description = 'Wizard to import supplier invoices as PDF'

    pdf_file = fields.Binary(
        string='Supplier PDF Invoice', required=True)
    pdf_filename = fields.Char(string='Filename')

    @api.model
    def parse_invoice(self):
        fd, file_name = mkstemp()
        try:
            os.write(fd, base64.decodestring(self.pdf_file))
        finally:
            os.close(fd)
        try:
            res = extract_data(file_name)
        except:
            raise UserError(_(
                "PDF Invoice parsing failed."))
        logger.info('Result of invoice2data PDF extraction: %s', res)
        prec = self.env['decimal.precision'].precision_get('Account')
        for entry in ['amount_untaxed', 'amount']:
            if res.get(entry):
                res[entry] = round(res[entry], prec)
        return res
        return {
            # 'currency_iso': 'EUR',
            'currency_symbol': u'€',  # The one or the other
            'date': datetime.strptime('2015-10-08', '%Y-%m-%d'),
            # must be in datetime
            'date_due': datetime.strptime('2015-11-07', '%Y-%m-%d'),
            'amount_untaxed': 10.0,
            'amount': 12.0,  # Total with taxes
            'vat': 'FR25499247138',
            'invoice_number': 'I1501243',
            'description': 'TGV Paris-Lyon',
        }

    @api.model
    def _select_partner(self, parsed_inv):
        if parsed_inv.get('vat'):
            vat = parsed_inv['vat'].replace(' ', '')
            partners = self.env['res.partner'].search([
                ('supplier', '=', True),
                ('is_company', '=', True),
                ('vat', '=', vat),
                ('invoice_import_id', '!=', False),
                ])
            if partners:
                return partners[0]
            else:
                raise UserError(_(
                    "The analysis of the PDF invoice returned '%s' as "
                    "supplier VAT number. But there are no supplier "
                    "with this VAT number and with an "
                    "Invoice Import Configuration in Odoo.") % vat)
        else:
            raise UserError(_(
                "PDF Invoice parsing didn't return the VAT number of the "
                "supplier."))

    @api.model
    def _prepare_invoice_vals(self, parsed_inv, partner):
        aio = self.env['account.invoice']
        ailo = self.env['account.invoice.line']
        company = self.env.user.company_id
        vals = {
            'partner_id': partner.id,
            'type': 'in_invoice',
            'company_id': company.id,
            'supplier_invoice_number':
            parsed_inv.get('invoice_number'),
            'date_invoice': parsed_inv.get('date'),
            'journal_id':
            aio.with_context(type='in_invoice')._default_journal().id,
            'invoice_line': [],
            'check_total': parsed_inv.get('amount'),
            }
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
        if currency:
            vals['currency_id'] = currency.id
        # otherwise, it will take the currency of the company

        vals.update(aio.onchange_partner_id(
            'in_invoice', partner.id, company_id=company.id)['value'])
        # Force due date of the invoice
        if parsed_inv.get('date_due'):
            vals['date_due'] = parsed_inv.get('date_due')
        config = partner.invoice_import_id
        if config.invoice_line_method == 'no_product':
            il_vals = {
                'name': config.label or
                parsed_inv.get('description', _('MISSING DESCRIPTION')),
                'account_id': config.account_id.id,
                'account_analytic_id': config.account_analytic_id.id or False,
                'invoice_line_tax_id': config.tax_ids.ids or False,
                'price_unit': parsed_inv.get('amount_untaxed'),
                }
        elif config.invoice_line_method == 'static_product':
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
            if config.account_analytic_id:
                il_vals['account_analytic_id'] = config.account_analytic_id.id
        self.set_price_unit_and_quantity(il_vals, parsed_inv)
        if il_vals.get('invoice_line_tax_id'):
            il_vals['invoice_line_tax_id'] = [
                (6, 0, il_vals['invoice_line_tax_id'])]
        vals['invoice_line'] = [(0, 0, il_vals)]
        return vals

    @api.model
    def set_price_unit_and_quantity(self, il_vals, parsed_inv):
        '''For the moment, we only take into account the 'price_include'
        option of the first tax'''
        il_vals['quantity'] = 1
        il_vals['price_unit'] = parsed_inv.get('amount')
        if il_vals.get('invoice_line_tax_id'):
            first_tax = self.env['account.tax'].browse(
                il_vals['invoice_line_tax_id'][0])
            if not first_tax.price_include:
                il_vals['price_unit'] = parsed_inv.get('amount_untaxed')

    @api.multi
    def import_invoice(self):
        self.ensure_one()
        logger.info('Starting to import PDF invoice')
        aio = self.env['account.invoice']
        parsed_inv = self.parse_invoice()
        partner = self._select_partner(parsed_inv)
        vals = self._prepare_invoice_vals(
            parsed_inv, partner)
        invoice = aio.create(vals)
        invoice.button_reset_taxes()

        # Force tax amount if necessary
        prec = self.env['decimal.precision'].precision_get('Account')
        if (
                parsed_inv.get('amount') and
                parsed_inv.get('amount_untaxed') and
                float_compare(
                    invoice.amount_total,
                    parsed_inv['amount'],
                    precision_digits=prec)):
            assert invoice.tax_line, 'Invoice has no tax line'
            initial_tax_amount = invoice.tax_line[0].amount
            tax_amount = parsed_inv['amount'] - parsed_inv['amount_untaxed']
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
        logger.info('End of the import of the PDF invoice')
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account', 'action_invoice_tree2')
        action.update({
            'view_mode': 'form,tree,calendar,graph',
            'views': False,
            'res_id': invoice.id,
            })
        return action
