# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("quantity")
    def _compute_price_unit(self):
        if self._context.get("aml_no_recompute_price_unit", False):
            return
        return super()._compute_price_unit()
