# Copyright 2017-2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    original_price_unit = fields.Monetary(
        help="Store price unit from every line when the "
        "invoice is created or the conversion is called "
        "for the first time to use it to convert the "
        "amount in the new currency.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("original_price_unit", vals.get("price_unit"))
        return super().create(vals_list)

    def _set_original_price_unit(self):
        for line in self:
            line.write({"original_price_unit": line.price_unit})
