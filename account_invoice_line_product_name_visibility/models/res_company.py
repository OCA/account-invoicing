from odoo import fields, models

from odoo.addons.base.models.res_company import company_default_for


class ResCompany(models.Model):
    _inherit = "res.company"

    hide_product_name = fields.Boolean(
        **company_default_for(
            "hide_product_name", "product.template", "hide_product_name"
        ),
    )
