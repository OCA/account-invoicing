# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends(
        "line_ids.amount_currency",
        "line_ids.tax_base_amount",
        "line_ids.tax_line_id",
        "partner_id",
        "currency_id",
        "amount_total",
        "amount_untaxed",
    )
    def _compute_tax_totals_json(self):
        """
        Allow tax edition for sale document in draft state
        """
        res = super()._compute_tax_totals_json()
        for move in self:
            if move.is_sale_document(include_receipts=True) and move.state == "draft":
                tax_totals = json.loads(move.tax_totals_json)
                tax_totals["allow_tax_edition"] = True
                move.tax_totals_json = json.dumps(tax_totals)
        return res
