# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        result = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        result['partner_bank_id'] = False
        if key[0].default_company_bank_id:
            bank_id = key[0].default_company_bank_id
            result['partner_bank_id'] = bank_id.id
        return result
