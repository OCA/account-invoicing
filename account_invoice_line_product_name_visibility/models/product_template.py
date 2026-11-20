from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hide_product_name = fields.Boolean(company_dependent=True)
