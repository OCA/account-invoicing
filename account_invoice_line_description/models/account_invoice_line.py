# -*- coding: utf-8 -*-
# Copyright 2015 Agile Business Group sagl
# (<http://www.agilebg.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if not self.user_has_groups(
                'account_invoice_line_description.'
                'group_use_product_description_per_inv_line'):
            return res

        if self.product_id:
            inv_type = self.invoice_id.type
            product = self.product_id.with_context(
                lang=self.invoice_id.partner_id.lang)
            self.name = (product.description_purchase or self.name if
                         inv_type in ('in_invoice', 'in_refund') else
                         product.description_sale or self.name)
        return res
