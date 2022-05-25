# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    journal_tmpl_id = fields.Many2one(
        comodel_name="account.product.move", string="Product Journal", readonly=True,
    )
