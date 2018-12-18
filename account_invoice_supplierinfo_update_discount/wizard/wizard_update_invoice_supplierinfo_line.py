# coding: utf-8
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _inherit = 'wizard.update.invoice.supplierinfo.line'

    current_discount = fields.Float(
        string='Current Discount', digits=dp.get_precision('Discount'),
        readonly=True)

    new_discount = fields.Float(
        string='New Discount', digits=dp.get_precision('Discount'),
        required=True)

    @api.multi
    def _prepare_supplierinfo(self, create=False):
        res = super(WizardUpdateInvoiceSupplierinfoLine, self).\
            _prepare_supplierinfo(create=create)
        res['discount'] = self.new_discount
        return res
