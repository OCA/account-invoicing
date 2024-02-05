# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
    _inherit = 'wizard.update.invoice.supplierinfo'

    display_discount = fields.Boolean(
        compute="_compute_display_discount",
    )

    @api.depends("line_ids.current_discount", "line_ids.new_discount")
    def _compute_display_discount(self):
        for wizard in self:
            wizard.display_discount = (
                any(wizard.mapped("line_ids.current_discount"))
                or any(wizard.mapped("line_ids.new_discount"))
            )
