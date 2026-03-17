# Copyright 2026 ACSONE SA/NV, BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_product_packaging_domain(self):
        domain = super()._get_product_packaging_domain()
        if self.move_id.is_purchase_document(include_receipts=True):
            domain.append(("purchase", "=", True))
        return domain
