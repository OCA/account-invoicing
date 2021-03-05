# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def get_taxes_values(self):
        lines = self.invoice_line_ids
        prev_values = lines.triple_discount_preprocess()
        tax_grouped = super().get_taxes_values()
        lines.triple_discount_postprocess(prev_values)
        return tax_grouped


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
