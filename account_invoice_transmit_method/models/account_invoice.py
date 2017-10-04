# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transmit_method_id = fields.Many2one(
        'transmit.method', string='Transmission Method',
        track_visibility='onchange', ondelete='restrict')  # domain in the view
    # Field used to match specific invoice transmit method
    # to show/display fields/buttons, add constraints, etc...
    transmit_method_code = fields.Char(
        related='transmit_method_id.code', readonly=True, store=True)

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if partner_id and type:
            partner = self.env['res.partner'].browse(partner_id)
            if type in ('out_invoice', 'out_refund'):
                res['value']['transmit_method_id'] =\
                    partner.customer_invoice_transmit_method_id.id or False
            else:
                res['value']['transmit_method_id'] =\
                    partner.supplier_invoice_transmit_method_id.id or False
        else:
            res['value']['transmit_method_id'] = False
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
