# -*- coding: utf-8 -*-
# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2014 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode='refund'):
        result = super(AccountInvoiceRefund, self).compute_refund(mode)
        active_ids = self.env.context.get('active_ids')
        if not active_ids:  # pragma: no cover
            return result
        # An example of result['domain'] computed by the parent wizard is:
        # [('type', '=', 'out_refund'), ('id', 'in', [43L, 44L])]
        # The created refund invoice is the first invoice in the
        # ('id', 'in', ...) tupla
        created_inv = [x[2] for x in result['domain']
                       if x[0] == 'id' and x[1] == 'in'][0]
        if mode == 'modify':
            # Remove pairs ids, because they are new draft invoices
            del created_inv[1::2]
        if created_inv:
            description = self[0].description or ''
            for idx, refund_id in enumerate(created_inv):
                origin_inv_id = active_ids[idx]
                refund = self.env['account.invoice'].browse(refund_id)
                refund.write({
                    'origin_invoice_ids': [(6, 0, [origin_inv_id])],
                    'refund_reason': description,
                })
                # Try to match refund invoice lines with original invoice lines
                origin_inv = self.env['account.invoice'].browse(origin_inv_id)
                refund.match_origin_lines(origin_inv)

        return result
