# Copyright 2016-Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _inherit = "wizard.update.invoice.supplierinfo.line"

    current_discount = fields.Float(
        string="Current Discount",
        digits="Discount",
        readonly=True,
    )

    new_discount = fields.Float(
        string="New Discount",
        digits="Discount",
        required=True,
    )

    def _prepare_supplierinfo_update(self):
        res = super()._prepare_supplierinfo_update()
        res["discount"] = self.new_discount
        return res
