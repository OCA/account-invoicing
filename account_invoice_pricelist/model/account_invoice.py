# -*- coding: utf-8 -*-
# © 2014-2016 GRAP <http://www.grap.coop>.
# © 2017 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later <http://www.gnu.org/licenses/agpl.html>.
from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Column Section
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist', string='Pricelist',
        help="The pricelist of the partner, when the invoice is created"
             " or the partner has changed."
    )

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False, payment_term=False,
            partner_bank_id=False, company_id=False):
        partner_obj = self.env['res.partner']
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        pricelist_id = False
        if partner_id:
            partner = partner_obj.browse(partner_id)
            if type in ('out_invoice', 'out_refund'):
                # Customer Invoices
                pricelist_id = partner.property_product_pricelist.id
            elif type in ('in_invoice', 'in_refund'):
                # Supplier Invoices
                if partner._model._columns.get(
                        'property_product_pricelist_purchase', False):
                    pricelist_id =\
                        partner.property_product_pricelist_purchase.id
        res['value']['pricelist_id'] = pricelist_id
        return res

    @api.model
    def _prepare_refund(
            self, invoice, date=None, period_id=None, description=None,
            journal_id=None):
        """Pricelist should also be set on refund."""
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date=date, period_id=period_id,
            description=description, journal_id=journal_id)
        if invoice.pricelist_id:
            values.update({
                'pricelist_id': invoice.pricelist_id.id,
            })
        return values

    @api.multi
    def button_update_prices_from_pricelist(self):
        for this in self:
            if this.state != 'draft':
                continue  # Should only be valid for draft invoices
            this.invoice_line.filtered('product_id').update_from_pricelist()
            this.button_reset_taxes()
