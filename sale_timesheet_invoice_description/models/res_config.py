# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_timesheet_invoice_description = fields.Selection(
        '_get_timesheet_invoice_description',
        "Timesheet Invoice Description")

    @api.model
    def _get_timesheet_invoice_description(self):
        return self.env['sale.order']._get_timesheet_invoice_description()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        default_timesheet_inv_desc = IrDefault.get(
            'sale.order',
            'timesheet_invoice_description'
        ) or '111'
        res.update(
            default_timesheet_invoice_description=default_timesheet_inv_desc,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set(
            'sale.order',
            'timesheet_invoice_description',
            self.default_timesheet_invoice_description)
