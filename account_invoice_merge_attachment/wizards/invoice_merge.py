# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class InvoiceMerge(models.TransientModel):

    _inherit = 'invoice.merge'

    link_attachment = fields.Boolean(default=True)

    @api.multi
    def merge_invoices(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        if self.link_attachment:
            ctx['link_attachment'] = True
        return super(InvoiceMerge, self.with_context(ctx)).merge_invoices()
