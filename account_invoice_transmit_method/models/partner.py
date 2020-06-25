# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_invoice_transmit_method_ids = fields.Many2many(
        'transmit.method', string='Customer Invoice Transmission Methods',
        relation='res_partner_customer_transmit_method',
        track_visibility='onchange',
        domain="[('customer_ok', '=', True)]",
    )
    customer_invoice_transmit_method_id = fields.Many2one(
        'transmit.method', string='Customer Invoice Transmission Method',
        compute='_compute_customer_invoice_transmit_method',
        inverse='_inverse_customer_invoice_transmit_method',
        store=True,
    )  # TODO: Delete on 13.0
    customer_invoice_transmit_method_code = fields.Char(
        related='customer_invoice_transmit_method_id.code',
        string='Customer Invoice Transmission Method Code', readonly=True
    )  # TODO: Delete on 13.0
    supplier_invoice_transmit_method_ids = fields.Many2many(
        'transmit.method',
        relation='res_partner_supplier_transmit_method',
        string='Supplier Invoice Transmission Methods',
        track_visibility='onchange',
        domain="[('supplier_ok', '=', True)]",
    )
    supplier_invoice_transmit_method_id = fields.Many2one(
        'transmit.method',
        string='Supplier Invoice Transmission Method',
        compute='_compute_supplier_invoice_transmit_method',
        inverse='_inverse_supplier_invoice_transmit_method',
        store=True,
    )
    supplier_invoice_transmit_method_code = fields.Char(
        related='supplier_invoice_transmit_method_id.code',
        string='Vendor Invoice Reception Method Code', readonly=True
    )

    @api.depends(
        'supplier_invoice_transmit_method_ids'
    )
    def _compute_supplier_invoice_transmit_method(self):
        for r in self:
            method = False
            if len(r.supplier_invoice_transmit_method_ids) == 1:
                method = r.supplier_invoice_transmit_method_ids
            r.supplier_invoice_transmit_method_id = method

    @api.depends(
        'customer_invoice_transmit_method_ids',
    )
    def _compute_customer_invoice_transmit_method(self):
        for r in self:
            method = False
            if len(r.customer_invoice_transmit_method_ids) == 1:
                method = r.customer_invoice_transmit_method_ids
            r.customer_invoice_transmit_method_id = method

    def _inverse_customer_invoice_transmit_method(self):
        for rec in self:
            rec.customer_invoice_transmit_method_ids =\
                rec.customer_invoice_transmit_method_id

    def _inverse_supplier_invoice_transmit_method(self):
        for rec in self:
            rec.supplier_invoice_transmit_method_ids =\
                rec.supplier_invoice_transmit_method_id

    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + [
            'customer_invoice_transmit_method_ids',
            'supplier_invoice_transmit_method_ids']
