# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class account_invoice(models.Model):
    _inherit = "account.invoice"

    is_deposit = fields.Boolean('Advance', readonly=True)

    @api.multi
    def action_cancel(self):
        """ For Advance (is_deposit=True), do not allow cancellation
        if advance amount has been deducted on following invoices"""
        for inv in self:
            # Other invoices exists
            if inv.is_deposit and inv.sale_ids.invoiced_rate:
                raise except_orm(
                    _('Warning!'),
                    _("""Cancellation of advance invoice is not allowed!
                    Please cancel all following invoices first."""))
        res = super(account_invoice, self).action_cancel()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
