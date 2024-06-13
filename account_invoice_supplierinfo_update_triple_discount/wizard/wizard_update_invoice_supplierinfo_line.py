# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _inherit = "wizard.update.invoice.supplierinfo.line"

    current_discount2 = fields.Float(
        string="Current Disc. 2 (%)", readonly=True, digits="Discount"
    )

    new_discount2 = fields.Float(
        string="New Disc. 2 (%)", required=True, digits="Discount"
    )

    current_discount3 = fields.Float(
        string="Current Disc. 3 (%)", readonly=True, digits="Discount"
    )

    new_discount3 = fields.Float(
        string="New Disc. 3 (%)", required=True, digits="Discount"
    )

    def _prepare_supplierinfo_update(self):
        res = super()._prepare_supplierinfo_update()
        res["discount2"] = self.new_discount2
        res["discount3"] = self.new_discount3
        return res

    def _get_fields_depend_current_cost(self):
        res = super()._get_fields_depend_current_cost()
        res += ["current_discount2", "current_discount3"]
        return res

    def _get_fields_depend_new_cost(self):
        res = super()._get_fields_depend_new_cost()
        res += ["new_discount2", "new_discount3"]
        return res

    def _compute_current_cost(self):
        super()._compute_current_cost()
        for line in self.filtered(lambda x: x.supplierinfo_id and x.current_discount):
            line.current_cost = (
                line.current_cost
                * (100 - line.current_discount2)
                / 100
                * (100 - line.current_discount3)
                / 100
            )
        return

    def _compute_new_cost(self):
        super()._compute_new_cost()
        for line in self:
            line.new_cost = (
                line.new_cost
                * (100 - line.new_discount2)
                / 100
                * (100 - line.new_discount3)
                / 100
            )
        return
