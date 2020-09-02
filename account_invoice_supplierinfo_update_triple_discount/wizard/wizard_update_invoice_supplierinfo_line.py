# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _inherit = 'wizard.update.invoice.supplierinfo.line'

    current_discount2 = fields.Float(
        string='Current Disc. 2 (%)', readonly=True,
        digits=dp.get_precision('Discount'))

    new_discount2 = fields.Float(
        string='New Disc. 2 (%)', required=True,
        digits=dp.get_precision('Discount'))

    current_discount3 = fields.Float(
        string='Current Disc. 3 (%)', readonly=True,
        digits=dp.get_precision('Discount'))

    new_discount3 = fields.Float(
        string='New Disc. 3 (%)', required=True,
        digits=dp.get_precision('Discount'))

    @api.multi
    def _prepare_supplierinfo_update(self):
        res = super()._prepare_supplierinfo_update()
        res['discount2'] = self.new_discount2
        res['discount3'] = self.new_discount3
        return res
