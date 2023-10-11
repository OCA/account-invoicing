# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_type = fields.Boolean(
        help="Define is the product will be used as a purchase type",
        index=True,
    )

    @api.onchange("purchase_type")
    def _onchange_purchase_type(self):
        """
        Onchange function for purchase_type field.
        When this purchase_type become to True, we have to set to True the
        purchase_ok field to allow it into the purchase invoice/refund.
        We also set to False the field sale_ok
        :return:
        """
        if self.purchase_type:
            self.purchase_ok = self.purchase_type
            self.sale_ok = False
