# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class InvoiceMerge(models.TransientModel):

    _inherit = 'invoice.merge'

    link_attachment = fields.Boolean(string="Link attachments", default=True)

    @api.multi
    def merge_invoices(self):
        self.ensure_one()
        return super(InvoiceMerge, self.with_context(
            link_attachment=self.link_attachment
        )).merge_invoices()
