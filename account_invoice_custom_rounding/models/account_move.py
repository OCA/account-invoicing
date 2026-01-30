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
        related=False,
        readonly=False,
        help="How total tax amount is computed. If no value selected, "
        "the method defined in the company is used.",
    )

    @api.depends("partner_id")
    def _compute_tax_calculation_rounding_method(self):
        for move in self:
            tax_calculation_rounding_method = (
                move.company_id.tax_calculation_rounding_method
            )
            if (
                move.is_invoice()
                and move.partner_id
                and move.partner_id.tax_calculation_rounding_method
            ):
                tax_calculation_rounding_method = (
                    move.partner_id.tax_calculation_rounding_method
                )
            move.tax_calculation_rounding_method = tax_calculation_rounding_method
