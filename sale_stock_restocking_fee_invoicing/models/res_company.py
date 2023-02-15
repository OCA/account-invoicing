# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    restocking_fee_product_id = fields.Many2one(
        "product.product",
        string="Restocking Fee Product",
        ondelete="restrict",
        default=lambda a: a._default_restocking_fee_product_id(),
        domain=[("type", "=", "service")],
        help="It is possible to specify on a customer whether restocking fee "
        "must be charged for returning goods. In the case where fee are to "
        "be applied, the product specified here is added to the sale"
        " order to charge these restocking fee.",
    )

    @api.model
    def _default_restocking_fee_product_id(self):
        product = self.env.ref(
            "sale_stock_restocking_fee_invoicing." "product_restocking_fee",
            raise_if_not_found=False,
        )
        if product:
            return product
        return None
