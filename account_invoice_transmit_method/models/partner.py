# Copyright 2017-2020 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_invoice_transmit_method_id = fields.Many2one(
        'transmit.method', string='Customer Invoice Transmission Method',
        company_dependant=True, tracking=True,
        ondelete='restrict')
    customer_invoice_transmit_method_code = fields.Char(
        related='customer_invoice_transmit_method_id.code',
        string='Customer Invoice Transmission Method Code', readonly=True)
    supplier_invoice_transmit_method_id = fields.Many2one(
        'transmit.method', string='Vendor Invoice Reception Method',
        company_dependant=True, tracking=True,
        ondelete='restrict')
    supplier_invoice_transmit_method_code = fields.Char(
        related='supplier_invoice_transmit_method_id.code',
        string='Vendor Invoice Reception Method Code', readonly=True)

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + [
            'customer_invoice_transmit_method_id',
            'supplier_invoice_transmit_method_id']
