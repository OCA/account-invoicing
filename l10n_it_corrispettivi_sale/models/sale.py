# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_corrispettivi_sale(self):
        self.corrispettivi = self.partner_id.use_corrispettivi

    corrispettivi = fields.Boolean()

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.corrispettivi:
            invoice_vals['journal_id'] = self.env['account.journal'] \
                .get_corr_journal(self.company_id).id
        return invoice_vals
