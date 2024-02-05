# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
    _inherit = 'wizard.update.invoice.supplierinfo'

    display_discount2 = fields.Boolean(
        compute="_compute_display_discount2",
    )

    display_discount3 = fields.Boolean(
        compute="_compute_display_discount3",
    )

    @api.depends("line_ids.current_discount2", "line_ids.new_discount2")
    def _compute_display_discount2(self):
        for wizard in self:
            wizard.display_discount2 = (
                any(wizard.mapped("line_ids.current_discount2"))
                or any(wizard.mapped("line_ids.new_discount2"))
            )

    @api.depends("line_ids.current_discount3", "line_ids.new_discount3")
    def _compute_display_discount3(self):
        for wizard in self:
            wizard.display_discount3 = (
                any(wizard.mapped("line_ids.current_discount3"))
                or any(wizard.mapped("line_ids.new_discount3"))
            )
