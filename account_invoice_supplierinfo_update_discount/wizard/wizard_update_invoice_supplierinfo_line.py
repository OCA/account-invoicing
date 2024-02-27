# Copyright 2016-Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _inherit = "wizard.update.invoice.supplierinfo.line"

    current_discount = fields.Float(
        digits="Discount",
        readonly=True,
    )

    new_discount = fields.Float(
        digits="Discount",
        required=True,
    )

    def _prepare_supplierinfo_update(self):
        res = super()._prepare_supplierinfo_update()
        res["discount"] = self.new_discount
        return res

    def _get_fields_depend_current_cost(self):
        res = super()._get_fields_depend_current_cost()
        res.append("current_discount")
        return res

    def _get_fields_depend_new_cost(self):
        res = super()._get_fields_depend_new_cost()
        res.append("new_discount")
        return res

    def _compute_current_cost(self):
        super()._compute_current_cost()
        for line in self.filtered(lambda x: x.supplierinfo_id and x.current_discount):
            line.current_cost = line.current_cost * (100 - line.current_discount) / 100
        return

    def _compute_new_cost(self):
        super()._compute_new_cost()
        for line in self:
            line.new_cost = line.new_cost * (100 - line.new_discount) / 100
        return
