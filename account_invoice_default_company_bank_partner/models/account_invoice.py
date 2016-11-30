# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def onchange_partner_id(self, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False,
                            company_id=False):
        result = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=False,
            payment_term=payment_term,
            partner_bank_id=partner_bank_id, company_id=company_id)
        partner = self.env['res.partner'].browse(partner_id)
        result['value']['partner_bank_id'] = False
        if partner.default_company_bank_id:
            bank_id = partner.default_company_bank_id
            result['value']['partner_bank_id'] = bank_id
        return result
