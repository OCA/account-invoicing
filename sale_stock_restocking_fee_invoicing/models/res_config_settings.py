# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    restocking_fee_product_id = fields.Many2one(
        "product.product",
        string="Restocking Fee Product",
        related="company_id.restocking_fee_product_id",
        help="It is possible to specify on a customer whether fees must be "
        "charged for returning goods. In the case where fees are to "
        "be applied, the product specified here is added to the sale"
        " order to charge these fees.",
        default=lambda self: self.env.user.company_id.restocking_fee_product_id,
        readonly=False,
    )
