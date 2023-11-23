# Copyright 2023 Jarsa, (<https://www.jarsa.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_name(self):
        name = super()._get_computed_name()
        if self.product_id.default_code:
            name = name.replace(f"[{self.product_id.default_code}] ", "").strip()
        return name
