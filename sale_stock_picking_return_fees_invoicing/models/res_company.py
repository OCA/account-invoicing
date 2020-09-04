# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    customer_return_fees_product_id = fields.Many2one(
        "product.product",
        string="Customer Return Fees Product",
        required=True,
        ondelete="restrict",
        default=lambda a: a._default_customer_return_fees_product_id(),
        domain=[("product_type", "=", "service")],
        help="It is possible to specify on a customer whether fees must be "
        "charged for returning goods. In the case where fees are to "
        "be applied, the product specified here is added to the sale"
        " order to charge these fees.",
    )

    @api.model
    def _default_customer_return_fees_product_id(self):
        product = self.env.ref(
            "sale_stock_picking_return_fees_invoicing."
            "product_customer_return_fees",
            raise_if_not_found=False,
        )
        if product:
            return product
        return None
