# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockConfigSettings(models.TransientModel):

    _inherit = 'stock.config.settings'

    customer_return_fees_product_id = fields.Many2one(
        "product.product",
        string="Customer Return Fees Product",
        related="company_id.customer_return_fees_product_id",
        help="It is possible to specify on a customer whether fees must be "
             "charged for returning goods. In the case where fees are to "
             "be applied, the product specified here is added to the sale"
             " order to charge these fees.",
    )
