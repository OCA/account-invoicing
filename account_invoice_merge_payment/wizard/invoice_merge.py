# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class InvoiceMerge(models.TransientModel):
    _inherit = 'invoice.merge'

    @api.model
    def _dirty_check(self):
        res = super(InvoiceMerge, self)._dirty_check()
        ids = self._context['active_ids']
        invs = self.env['account.invoice'].browse(ids)
        for i, inv in enumerate(invs):
            if i > 0:
                if inv.payment_mode_id != invs[0].payment_mode_id:
                    raise UserError(
                        _('Not all invoices have the same Payment Mode!'))
        return res
