# -*- coding: utf-8 -*-
# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2014 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    refund_reason = fields.Text(string="Refund reason")
    origin_invoice_ids = fields.Many2many(
        comodel_name='account.invoice', column1='refund_invoice_id',
        column2='original_invoice_id', relation='account_invoice_refunds_rel',
        string="Original invoice", readonly=True,
        help="Original invoice to which this refund invoice is referred to")
    refund_invoice_ids = fields.Many2many(
        comodel_name='account.invoice', column1='original_invoice_id',
        column2='refund_invoice_id', relation='account_invoice_refunds_rel',
        string="Refund invoices",  readonly=True,
        help="Refund invoices created from this invoice")

    @api.multi
    def match_origin_lines(self, origin_inv):
        for idx, line in enumerate(origin_inv.invoice_line_ids):
            try:
                # Protect this write, maybe refund invoice doesn't
                # have the same lines than original one
                self.invoice_line_ids[idx].write({
                    'origin_line_ids': [(6, 0, line.ids)],
                })
            except:  # pragma: no cover
                pass
        return True
