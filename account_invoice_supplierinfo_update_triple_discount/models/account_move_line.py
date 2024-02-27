# Copyright (C) 2018-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _is_matching_supplierinfo(self, supplierinfo):
        res = super()._is_matching_supplierinfo(supplierinfo)
        return (
            res
            and self.discount2 == supplierinfo.discount2
            and self.discount3 == supplierinfo.discount3
        )

    def _prepare_supplier_wizard_line(self, supplierinfo):
        res = super()._prepare_supplier_wizard_line(supplierinfo)
        res["current_discount2"] = supplierinfo and supplierinfo.discount2
        res["new_discount2"] = self.discount2
        res["current_discount3"] = supplierinfo and supplierinfo.discount3
        res["new_discount3"] = self.discount3
        return res
