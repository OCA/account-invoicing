# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_supplier_wizard_line(self, supplierinfo):
        res = super()._prepare_supplier_wizard_line(supplierinfo)
        res["current_multiplier_qty"] = res["new_multiplier_qty"] = (
            supplierinfo and supplierinfo.multiplier_qty
        )
        return res
