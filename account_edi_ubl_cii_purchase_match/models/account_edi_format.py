# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiFormat(models.Model):

    _inherit = "account.edi.format"

    def _retrieve_product(self, name=None, default_code=None, barcode=None):
        product = super()._retrieve_product(
            name=name, default_code=default_code, barcode=barcode
        )
        if product:
            return product
        product_sinfo = self.env["product.supplierinfo"].search(
            [("product_code", "=", default_code)], limit=1
        )
        if product_sinfo and product_sinfo.product_id:
            return product_sinfo.product_id
        if (
            product_sinfo
            and product_sinfo.product_tmpl_id
            and len(product_sinfo.product_tmpl_id.product_variant_ids) == 1
        ):
            return product_sinfo.product_tmpl_id.product_variant_ids
        return product
