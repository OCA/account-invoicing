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

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        result = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id:
            if self.type in ('out_invoice', 'out_refund'):
                # Customer Invoices
                self.pricelist_id = self.partner_id.property_product_pricelist
            elif self.type in ('in_invoice', 'in_refund'):
                # Supplier Invoices
                if hasattr(self.partner_id,
                           'property_product_pricelist_purchase'):
                    self.pricelist_id =\
                        self.partner_id.property_product_pricelist_purchase
        return result

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        """Pricelist should also be set on refund."""
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if invoice.pricelist_id:
            values.update({
                'pricelist_id': invoice.pricelist_id.id,
            })
        return values

    @api.multi
    def button_update_prices_from_pricelist(self):
        for inv in self.filtered(lambda r: r.state == 'draft'):
            inv.invoice_line_ids.filtered('product_id').update_from_pricelist()
