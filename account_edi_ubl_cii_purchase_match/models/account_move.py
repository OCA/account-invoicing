# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _link_invoice_origin_to_purchase_orders(self, timeout=10):
        # disable standard purchase linking
        return self
