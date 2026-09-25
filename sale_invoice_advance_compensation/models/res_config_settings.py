# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_advance_journal_id = fields.Many2one(
        related="company_id.sale_advance_journal_id",
        readonly=False,
    )
    sale_advance_product_id = fields.Many2one(
        related="company_id.sale_advance_product_id",
        readonly=False,
    )
