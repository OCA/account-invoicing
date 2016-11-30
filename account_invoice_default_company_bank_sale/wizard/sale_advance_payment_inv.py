# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp import models, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _prepare_advance_invoice_vals(self):
        result = super(SaleAdvancePaymentInv,
                       self)._prepare_advance_invoice_vals()
        partner_id = result[0][1].get('partner_id')
        partner = self.env['res.partner'].search(
            [('id', '=', partner_id)])
        result[0][1].update({'partner_bank_id': False})
        if partner.default_company_bank_id:
            result[0][1].update(
                {'partner_bank_id':
                 partner.default_company_bank_id.id})
        return result
