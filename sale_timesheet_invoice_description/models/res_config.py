# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    default_timesheet_invoice_description = fields.Selection(
        '_get_timesheet_invoice_description',
        "Timesheet Invoice Description")

    @api.model
    def _get_timesheet_invoice_description(self):
        return self.env['sale.order']._get_timesheet_invoice_description()

    @api.model
    def get_default_sale_config(self, fields):
        default_timesheet_inv_desc = self.env['ir.values'].get_default(
            'sale.order', 'timesheet_invoice_description') or '1111'
        return {
            'default_timesheet_invoice_description':
                default_timesheet_inv_desc,
        }

    @api.multi
    def set_sale_defaults(self):
        self.ensure_one()
        self.env['ir.values'].sudo().set_default(
            'sale.order', 'timesheet_invoice_description',
            self.default_timesheet_invoice_description)
        res = super(SaleConfiguration, self).set_sale_defaults()
        return res
