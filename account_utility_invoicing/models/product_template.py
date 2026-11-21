# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    utility_ids = fields.One2many(
        comodel_name="res.utility",
        inverse_name="product_tmpl_id",
        domain=lambda self: self._get_domain_utility_ids(),
    )

    def _get_domain_utility_ids(self):
        base_domain = [("product_tmpl_id", "=", False)]
        has_company = "(company_id and [('company_id', 'in', [company_id, False])]"
        return f"{has_company} or [(1, '=', 1)]) + {base_domain}"
