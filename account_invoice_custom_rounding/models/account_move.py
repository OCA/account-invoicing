# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    tax_calculation_rounding_method = fields.Selection(
        [
            ("round_per_line", "Round per Line"),
            ("round_globally", "Round Globally"),
        ],
        compute="_compute_tax_calculation_rounding_method",
        store=True,
        readonly=False,
        help="How total tax amount is computed. If no value selected, "
        "the method defined in the company is used.",
    )

    @api.depends("partner_id")
    def _compute_tax_calculation_rounding_method(self):
        for move in self:
            tax_calculation_rounding_method = False
            if (
                move.is_invoice()
                and move.partner_id
                and move.partner_id.tax_calculation_rounding_method
            ):
                tax_calculation_rounding_method = (
                    move.partner_id.tax_calculation_rounding_method
                )
            move.tax_calculation_rounding_method = tax_calculation_rounding_method

    def _recompute_dynamic_lines(
        self, recompute_all_taxes=False, recompute_tax_base_amount=False
    ):
        for move in self.filtered(
            lambda a: a.is_invoice() and a.tax_calculation_rounding_method
        ):
            super(
                AccountMove,
                move.with_context(
                    round=move.tax_calculation_rounding_method == "round_per_line"
                ),
            )._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
        return super(
            AccountMove,
            self.filtered(
                lambda a: not (a.is_invoice() and a.tax_calculation_rounding_method)
            ),
        )._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)

    def write(self, vals):
        res = super().write(vals)
        if "tax_calculation_rounding_method" in vals:
            # Context added so the invoice can be saved when the rounding method
            # changes
            self.with_context(check_move_validity=False)._recompute_dynamic_lines(
                recompute_all_taxes=True
            )
        return res
