# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp.osv import osv


class mrp_repair(osv.osv):
    _inherit = 'mrp.repair'

    def action_invoice_create(self, cr, uid, ids, group=False, context=None):
        """ Creates invoice(s) for repair order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """

        res = super(mrp_repair, self).action_invoice_create(
            cr, uid, ids, group=group, context=context)
        invoice_obj = self.pool.get('account.invoice')

        for repair in self.browse(cr, uid, ids, context=context):
            inv_id = res[repair.id]
            rp = repair.partner_id
            rpi = repair.partner_invoice_id
            inv_vals = {'partner_bank_id': (rpi.default_company_bank_id.id or
                                            rp.default_company_bank_id.id)}
            invoice_obj.write(cr, uid, [inv_id], inv_vals, context=context)
        return res
