# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _inherit = 'wizard.update.invoice.supplierinfo.line'

    to_variant = fields.Boolean(
        string='Update to the variant',
        help='- Check the option for an update on the product variant.\n'
             '- Uncheck the option for an update on the product model.')

    @api.multi
    def _prepare_supplierinfo(self):
        if self.to_variant:
            return {
                'product_id': self.product_id.id,
                'name': self.wizard_id.invoice_id.supplier_partner_id.id,
                'min_qty': 0.0,
                'delay': 1,
            }
        return super(WizardUpdateInvoiceSupplierinfoLine,
                     self)._prepare_supplierinfo()
