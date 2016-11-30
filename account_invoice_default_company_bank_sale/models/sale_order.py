# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_invoice(self, order, lines):
        result = super(SaleOrder, self)._prepare_invoice(
            order, lines)
        partner = self.env['res.partner'].search(
            [('id', '=', result['partner_id'])])
        result['partner_bank_id'] = False
        if partner.default_company_bank_id:
            bank_id = partner.default_company_bank_id
            result['partner_bank_id'] = bank_id.id
        return result
