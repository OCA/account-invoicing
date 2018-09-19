# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_invoice_transmit_method_id = fields.Many2one(
        'transmit.method', string='Customer Invoice Transmission Method',
        company_dependent=True, track_visibility='onchange',
        domain=[('customer_ok', '=', True)], ondelete='restrict')
    customer_invoice_transmit_method_code = fields.Char(
        related='customer_invoice_transmit_method_id.code',
        string='Customer Invoice Transmission Method Code', readonly=True)
    supplier_invoice_transmit_method_id = fields.Many2one(
        'transmit.method', string='Vendor Invoice Reception Method',
        company_dependent=True, track_visibility='onchange',
        domain=[('supplier_ok', '=', True)], ondelete='restrict')
    supplier_invoice_transmit_method_code = fields.Char(
        related='supplier_invoice_transmit_method_id.code',
        string='Vendor Invoice Reception Method Code', readonly=True)

    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + [
            'customer_invoice_transmit_method_id',
            'supplier_invoice_transmit_method_id']
