# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transmit_method_ids = fields.Many2many(
        'transmit.method', string='Transmission Methods',
        track_visibility='onchange', ondelete='restrict')
    # domain in the view
    # Field used to match specific invoice transmit method
    # to show/display fields/buttons, add constraints, etc...
    transmit_method_id = fields.Many2one(
        'transmit.method', string='Transmission Method',
        store=True, compute='_compute_transmit_method',
        inverse='_inverse_transmit_method',
    )
    transmit_method_code = fields.Char(
        related='transmit_method_id.code', readonly=True, store=True
    )

    @api.depends('transmit_method_ids')
    def _compute_transmit_method(self):
        for record in self:
            method = False
            if len(record.transmit_method_ids) == 1:
                method = record.transmit_method_ids
            record.transmit_method_id = method

    def _inverse_transmit_method(self):
        if self.env.context.get('computing_transmit_method', False):
            return
        for record in self:
            record.transmit_method_ids = record.transmit_method_id

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and self.type:
            if self.type in ('out_invoice', 'out_refund'):
                self.transmit_method_ids = self.partner_id.\
                    customer_invoice_transmit_method_ids
            else:
                self.transmit_method_ids = self.partner_id.\
                    supplier_invoice_transmit_method_ids
        return res

    @api.model
    def create(self, vals):
        if (
                'transmit_method_ids' not in vals and
                vals.get('type') and
                vals.get('partner_id')):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if vals['type'] in ('out_invoice', 'out_refund'):
                vals['transmit_method_ids'] = [(
                    6, 0, partner.customer_invoice_transmit_method_ids.ids)]
            else:
                vals['transmit_method_ids'] = [(
                    6, 0, partner.supplier_invoice_transmit_method_ids.ids)]
        return super(AccountInvoice, self).create(vals)

    def _transmit_invoice(self):
        self.ensure_one()
        transmitted = False
        for transmit_method in self.transmit_method_ids:
            transmition_result = transmit_method._transmit_invoice(self)
            transmitted = transmitted or transmition_result
        return transmitted

    def action_invoice_sent(self):
        result = super().action_invoice_sent()
        result['context']['default_is_transmit'] = bool(
            self.transmit_method_ids)
        return result
