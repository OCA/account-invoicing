# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _inherit = 'wizard.update.invoice.supplierinfo.line'

    current_multiplier_qty = fields.Float(
        string='Current Multiplier Qty',
        readonly=True
    )

    new_multiplier_qty = fields.Float(
        string='New Multiplier Qty',
        required=True
    )

    @api.multi
    def _prepare_supplierinfo_update(self):
        res = super()._prepare_supplierinfo_update()
        res['multiplier_qty'] = self.new_multiplier_qty
        return res
