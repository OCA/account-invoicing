# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp import models, api

class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    @api.multi
    def action_invoice_create(self, group=False, context=None):
        """ Creates invoice(s) for repair order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """
        res = super(MrpRepair, self).action_invoice_create(
            group=group, context=context)
        invoice_obj = self.env['account.invoice']

        for repair in self:
            inv_id = res[repair.id]
            rp = repair.partner_id
            rpi = repair.partner_invoice_id
            inv_vals = {'partner_bank_id': (rpi.default_company_bank_id.id or
                                            rp.default_company_bank_id.id)}
            invoice_obj.browse(inv_id).write(inv_vals)
        return res
