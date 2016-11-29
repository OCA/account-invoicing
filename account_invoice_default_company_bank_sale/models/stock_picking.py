# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp.osv import osv


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        if context is None:
            context = {}
        partner, currency_id, company_id, user_id = key
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        return {
            'origin': move.picking_id.name,
            'date_invoice': context.get('date_inv', False),
            'user_id': user_id,
            'partner_id': partner.id,
            'partner_bank_id': partner.default_company_bank_id.id,
            'account_id': account_id,
            'payment_term': payment_term,
            'type': inv_type,
            'fiscal_position': partner.property_account_position.id,
            'company_id': company_id,
            'currency_id': currency_id,
            'journal_id': journal_id,
        }
