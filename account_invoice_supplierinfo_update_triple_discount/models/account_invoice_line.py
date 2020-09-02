# Copyright (C) 2018-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _is_correct_price(self, supplierinfo):
        res = super()._is_correct_price(supplierinfo)
        return res and\
            self.discount2 == supplierinfo.discount2 and\
            self.discount3 == supplierinfo.discount3

    @api.multi
    def _prepare_supplier_wizard_line(self, supplierinfo):
        res = super()._prepare_supplier_wizard_line(supplierinfo)
        res['current_discount2'] = supplierinfo and supplierinfo.discount2
        res['new_discount2'] = self.discount2
        res['current_discount3'] = supplierinfo and supplierinfo.discount3
        res['new_discount3'] = self.discount3
        return res
