# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_cancel(self):

        res = super(SaleOrder, self).action_cancel()

        for order in self:
            # cancel order's invoices
            for invoice in order.invoice_ids:
                if invoice.state == 'draft':
                    invoice.state = 'cancel'
                elif invoice.state in ('paid', 'open'):
                    invoice.refund_cancel_order(order.name)

        return res
