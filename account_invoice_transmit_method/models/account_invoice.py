# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transmit_method_id = fields.Many2one(
        'transmit.method', string='Transmission Method',
        track_visibility='onchange', ondelete='restrict')  # domain in the view
    # Field used to match specific invoice transmit method
    # to show/display fields/buttons, add constraints, etc...
    transmit_method_code = fields.Char(
        related='transmit_method_id.code', readonly=True, store=True)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and self.type:
            if self.type in ('out_invoice', 'out_refund'):
                self.transmit_method_id = self.partner_id.\
                    customer_invoice_transmit_method_id.id or False
            else:
                self.transmit_method_id = self.partner_id.\
                    supplier_invoice_transmit_method_id.id or False
        else:
            self.transmit_method_id = False
        return res

    @api.model
    def create(self, vals):
        if (
                'transmit_method_id' not in vals and
                vals.get('type') and
                vals.get('partner_id')):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if vals['type'] in ('out_invoice', 'out_refund'):
                vals['transmit_method_id'] =\
                    partner.customer_invoice_transmit_method_id.id or False
            else:
                vals['transmit_method_id'] =\
                    partner.supplier_invoice_transmit_method_id.id or False
        return super(AccountInvoice, self).create(vals)
