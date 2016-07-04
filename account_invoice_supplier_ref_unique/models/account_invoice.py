# -*- coding: utf-8 -*-
# Copyright 2015 Akretion
# Copyright 2010 - 2014 Savoir-Faire-Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    supplier_invoice_number = fields.Char(copy=False)

    @api.one
    @api.constrains('supplier_invoice_number')
    def _check_unique_supplier_invoice_number_insensitive(self):
        if (
                self.supplier_invoice_number and
                self.type in ('in_invoice', 'in_refund')):
            same_supplier_inv_num = self.search([
                ('commercial_partner_id', '=', self.commercial_partner_id.id),
                ('type', 'in', ('in_invoice', 'in_refund')),
                ('supplier_invoice_number',
                 '=ilike',
                 self.supplier_invoice_number),
                ('id', '!=', self.id), ])
            if same_supplier_inv_num:
                raise ValidationError(
                    _("The invoice/refund with supplier invoice number '%s' "
                      "already exists in Odoo under the number '%s' "
                      "for supplier '%s'.") % (
                        same_supplier_inv_num[0].supplier_invoice_number,
                        same_supplier_inv_num[0].number or '-',
                        same_supplier_inv_num[0].partner_id.display_name))
