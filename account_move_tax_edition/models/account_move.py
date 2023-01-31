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
        """Computed field used for custom widget's rendering.
        Only set on invoices.
        """
        for move in self:
            if not move.is_invoice(include_receipts=True):
                # Non-invoice moves don't support that field (because of multicurrency:
                # all lines of the invoice share the same currency)
                move.tax_totals_json = None
                continue

            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()

            move.tax_totals_json = json.dumps(
                {
                    **self._get_tax_totals(
                        move.partner_id,
                        tax_lines_data,
                        move.amount_total,
                        move.amount_untaxed,
                        move.currency_id,
                    ),
                    "allow_tax_edition": (
                        move.is_purchase_document(include_receipts=False)
                        or move.is_sale_document(include_receipts=False)
                    )
                    and move.state == "draft",
                }
            )
