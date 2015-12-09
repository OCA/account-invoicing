# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def _prepare_cost_invoice(self, partner, company_id, currency_id,
                              analytic_lines):
        res = super(AccountAnalyticLine, self)._prepare_cost_invoice(
            partner, company_id, currency_id, analytic_lines)
        partner_invoice_id = partner.id
        if partner:
            addr_ids = partner.address_get(adr_pref=['invoice'])
            partner_invoice_id = addr_ids['invoice']
        res['partner_id'] = partner_invoice_id
        return res
