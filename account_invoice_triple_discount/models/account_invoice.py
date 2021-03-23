# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def get_taxes_values(self):
        lines = self.invoice_line_ids
        prev_values = lines.triple_discount_preprocess()
        tax_grouped = super().get_taxes_values()
        lines.triple_discount_postprocess(prev_values)
        return tax_grouped

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        self.ensure_one()
        res = super()._onchange_partner_id()
        partner_discounting_type = self.partner_id.discounting_type
        if partner_discounting_type:
            self.invoice_line_ids.update({
                'discounting_type': partner_discounting_type,
            })
        return res


class AccountInvoiceLine(models.Model):
    _name = "account.invoice.line"
    _inherit = ["line.triple_discount.mixin", "account.invoice.line"]

    @api.multi
    @api.depends('discount2', 'discount3', 'discounting_type')
    def _compute_price(self):
        for line in self:
            prev_values = line.triple_discount_preprocess()
            super(AccountInvoiceLine, line)._compute_price()
            line.triple_discount_postprocess(prev_values)
