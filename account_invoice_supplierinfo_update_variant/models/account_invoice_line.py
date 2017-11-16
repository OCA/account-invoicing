# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _prepare_supplier_wizard_line(self, supplierinfo, partnerinfo):
        res = super(AccountInvoiceLine, self)._prepare_supplier_wizard_line(
            supplierinfo, partnerinfo)
        if self.product_id.product_variant_count > 1:
            res['to_variant'] = True
        return res
