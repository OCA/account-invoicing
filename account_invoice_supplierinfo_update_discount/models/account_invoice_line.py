# coding: utf-8
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _is_correct_price(self, supplierinfo):
        res = super(AccountInvoiceLine, self)._is_correct_price(supplierinfo)
        return res and (self.discount == supplierinfo.discount)

    @api.multi
    def _prepare_supplier_wizard_line(self, supplierinfo):
        self.ensure_one()
        res = super(AccountInvoiceLine, self)._prepare_supplier_wizard_line(
            supplierinfo)
        res['current_discount'] = supplierinfo and supplierinfo.discount
        res['new_discount'] = self.discount
        return res
