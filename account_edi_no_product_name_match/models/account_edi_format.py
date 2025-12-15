# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


def _is_true(s):
    return s not in ("F", "False", "false", 0, "", None, False)


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _retrieve_product(self, name=None, default_code=None, barcode=None):
        product_name_match = _is_true(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account_edi.product_name_match")
        )
        if product_name_match:
            return super()._retrieve_product(
                name=name, default_code=default_code, barcode=barcode
            )
        return super()._retrieve_product(
            name=None, default_code=default_code, barcode=barcode
        )
