# Copyright 2016 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    supplier_invoice_number = fields.Char(
        string='Vendor invoice number',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False)

    @api.one
    @api.constrains('supplier_invoice_number')
    def _check_unique_supplier_invoice_number_insensitive(self):
        """
        Check if an other vendor bill has the same supplier_invoice_number
        and the same commercial_partner_id than the current instance
        """
        if self.supplier_invoice_number and\
                self.type in ('in_invoice', 'in_refund'):
            same_supplier_inv_num = self.search([
                ('commercial_partner_id', '=', self.commercial_partner_id.id),
                ('type', 'in', ('in_invoice', 'in_refund')),
                ('supplier_invoice_number',
                 '=ilike', self.supplier_invoice_number),
                ('id', '!=', self.id)
            ], limit=1)
            if same_supplier_inv_num:
                raise ValidationError(_(
                    "The invoice/refund with supplier invoice number '%s' "
                    "already exists in Odoo under the number '%s' "
                    "for supplier '%s'.") % (
                        same_supplier_inv_num.supplier_invoice_number,
                        same_supplier_inv_num.number or '-',
                        same_supplier_inv_num.partner_id.display_name))

    @api.onchange('supplier_invoice_number')
    def _onchange_supplier_invoice_number(self):
        if not self.reference:
            self.reference = self.supplier_invoice_number

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None,
                        date=None, description=None, journal_id=None):
        """
        The unique vendor invoice number cannot be passed to the credit note
        in vendor bills
        """
        vals = super()._prepare_refund(
            invoice, date_invoice, date, description, journal_id)

        if invoice and invoice.type in ['in_invoice', 'in_refund'] and\
                'reference' in vals:
            vals['reference'] = ''

        return vals

    @api.multi
    def copy(self, default=None):
        """
        The unique vendor invoice number is not copied in vendor bills
        """
        if self.type in ['in_invoice', 'in_refund']:
            default = dict(default or {}, reference='')
        return super().copy(default)
