# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import Warning as UserError
import logging

logger = logging.getLogger(__name__)


class BusinessDocumentImport(models.AbstractModel):
    _name = 'business.document.import'
    _description = 'Common methods to import business documents'

    @api.model
    def _match_partner(self, parsed_inv, partner_type='supplier'):
        if parsed_inv.get('partner'):
            return parsed_inv['partner']
        if parsed_inv.get('partner_vat'):
            vat = parsed_inv['partner_vat'].replace(' ', '').upper()
            # use base_vat_sanitized
            partners = self.env['res.partner'].search([
                (partner_type, '=', True),
                ('parent_id', '=', False),
                ('sanitized_vat', '=', vat)])
            if partners:
                return partners[0]
            else:
                # TODO: update error msg
                raise UserError(_(
                    "The analysis of the invoice returned '%s' as "
                    "partner VAT number. But there are no supplier "
                    "with this VAT number in Odoo.") % vat)
        if parsed_inv.get('partner_email'):
            partners = self.env['res.partner'].search([
                ('email', '=ilike', parsed_inv['partner_email']),
                (partner_type, '=', True)])
            if partners:
                return partners[0].commercial_partner_id
        if parsed_inv.get('partner_name'):
            partners = self.env['res.partner'].search([
                ('name', '=ilike', parsed_inv['partner_name']),
                ('is_company', '=', True),
                (partner_type, '=', True)])
            if partners:
                return partners[0]
        raise UserError(_(
            "Invoice parsing didn't return the VAT number of the "
            "partner. In this case, invoice parsing should return the "
            "email or the name of the partner, but it was not returned "
            "or it was returned but it didn't match any "
            "existing partner."))
        # TODO : now that we use it for sale order, we may not want to
        # always return a parent partner

    @api.model
    def _match_product(self, parsed_line, partner=False):
        """This method is designed to be inherited"""
        ppo = self.env['product.product']
        if parsed_line.get('product'):
            return parsed_line['product']
        if parsed_line.get('product_ean13'):
            # Don't filter on purchase_ok = 1 because we don't depend
            # on the purchase module
            products = ppo.search([
                ('ean13', '=', parsed_line['product_ean13'])])
            if products:
                return products[0]
        if parsed_line.get('product_code'):
            # Should probably be modified to match via the supplier code
            products = ppo.search(
                [('default_code', '=', parsed_line['product_code'])])
            if products:
                return products[0]
            # WARNING: Won't work for multi-variant products
            # because product.supplierinfo is attached to product template
            if partner:
                sinfo = self.env['product.supplierinfo'].search([
                    ('name', '=', partner.id),
                    ('product_code', '=', parsed_line['product_code']),
                    ])
                if (
                        sinfo and
                        sinfo[0].product_tmpl_id.product_variant_ids and
                        len(
                        sinfo[0].product_tmpl_id.product_variant_ids) == 1
                        ):
                    return sinfo[0].product_tmpl_id.product_variant_ids[0]
        raise UserError(_(
            "Could not find any corresponding product in the Odoo database "
            "with EAN13 '%s' or Default Code '%s' or "
            "Supplier Product Code '%s' with supplier '%s'.") % (
                parsed_line.get('product_ean13'),
                parsed_line.get('product_code'),
                parsed_line.get('product_code'),
                partner and partner.name or 'None'))

    @api.model
    def _match_currency(self, parsed_inv):
        if parsed_inv.get('currency'):
            return parsed_inv['currency']
        if parsed_inv.get('currency_iso'):
            currency_iso = parsed_inv['currency_iso'].upper()
            currencies = self.env['res.currency'].search(
                [('name', '=', currency_iso)])
            if currencies:
                return currencies[0]
            else:
                raise UserError(_(
                    "The analysis of the invoice returned '%s' as "
                    "the currency ISO code. But there are no currency "
                    "with that name in Odoo.") % currency_iso)
        if parsed_inv.get('currency_symbol'):
            cur_symbol = parsed_inv['currency_symbol']
            currencies = self.env['res.currency'].search(
                [('symbol', '=', cur_symbol)])
            if currencies:
                return currencies[0]
            else:
                raise UserError(_(
                    "The analysis of the invoice returned '%s' as "
                    "the currency symbol. But there are no currency "
                    "with that symbol in Odoo.") % cur_symbol)
        return self.env.user.company_id.currency_id
