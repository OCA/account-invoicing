# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_advance_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Default Advance Journal",
        check_company=True,
        domain="[('company_id', '=', id), ('type', '=', 'sale')]",
    )
    sale_advance_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Default Advance Product",
        check_company=True,
        domain="[('type', '=', 'service')]",
    )
