# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _inverse_tax_totals(self):
        res = super()._inverse_tax_totals()
        with self._disable_recursion(
            {"records": self}, "skip_invoice_sync"
        ) as disabled:
            if disabled:
                return
        with self._sync_dynamic_line(
            existing_key_fname="term_key",
            needed_vals_fname="needed_terms",
            needed_dirty_fname="needed_terms_dirty",
            line_type="payment_term",
            container={"records": self},
        ):
            for move in self:
                invoice_totals = move.tax_totals
                if move.is_invoice(include_receipts=True) or not invoice_totals:
                    continue

                for subtotal in invoice_totals["subtotals"]:
                    for tax_group in subtotal["tax_groups"]:
                        tax_lines = move.line_ids.filtered(
                            lambda line, tax_group=tax_group: line.tax_group_id.id
                            == tax_group["id"]
                        )

                        if tax_lines:
                            first_tax_line = tax_lines[0]
                            tax_group_old_amount = sum(
                                tax_lines.mapped("amount_currency")
                            )
                            sign = -1 if move.is_inbound() else 1
                            delta_amount = (
                                tax_group_old_amount * sign
                                - tax_group["tax_amount_currency"]
                            )

                            if not move.currency_id.is_zero(delta_amount):
                                first_tax_line.amount_currency -= delta_amount * sign
            self._compute_amount()
        return res
