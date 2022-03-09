# Copyright 2016-Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _is_correct_price(self, supplierinfo):
        res = super()._is_correct_price(supplierinfo)
        return res and (self.discount == supplierinfo.discount)

    def _prepare_supplier_wizard_line(self, supplierinfo):
        res = super()._prepare_supplier_wizard_line(supplierinfo)
        res["current_discount"] = supplierinfo and supplierinfo.discount
        res["new_discount"] = self.discount
        return res
