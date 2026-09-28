# Copyright 2026 ACSONE SA/NV,BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    tax_domain = fields.Binary(compute="_compute_tax_domain")

    @api.depends(
        "account_id",
        "move_id.invoice_filter_type_domain",
        "move_id.company_id",
        "move_id.tax_country_id",
    )
    def _compute_tax_domain(self):
        for rec in self:
            domain = [
                ("type_tax_use", "=?", rec.move_id.invoice_filter_type_domain),
                ("company_id", "=", rec.move_id.company_id.id),
                ("country_id", "=", rec.move_id.tax_country_id.id),
            ]
            if not rec.account_id:
                rec.tax_domain = domain
                continue
            taxes = self.env["account.tax"].search(domain)
            allowed_taxes = taxes._filter_allowed_for_account(rec.account_id)
            rec.tax_domain = [("id", "in", allowed_taxes.ids)]
