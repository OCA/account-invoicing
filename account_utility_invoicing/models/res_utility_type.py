# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ResUtilityType(models.Model):
    _name = "res.utility.type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Utility Type"
    _rec_names_search = ["code", "name"]

    name = fields.Char(
        required=True,
        tracking=True,
        translate=True,
    )
    code = fields.Char(
        tracking=True,
    )
    utility_ids = fields.One2many(
        comodel_name="res.utility",
        inverse_name="utility_type_id",
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
    )
    base_rate = fields.Float(
        digits="Energy Rate",
        help="Base price per unit (e.g. per kWh)",
        tracking=True,
    )
    adjustment_rate = fields.Float(
        digits="Energy Rate",
        help="Adjustment rate applied to electricity cost per kWh (e.g., FT, PCA).",
        tracking=True,
    )
    total_rate = fields.Float(
        digits="Energy Rate",
        compute="_compute_total_rate",
        store=True,
        help="Total rate is the sum of base rate and adjustment rate.",
    )
    alert_threshold = fields.Integer(
        string="Alert Threshold (%)",
        tracking=True,
        help=(
            "Percentage increase compared to the previous reading that will "
            "trigger a visual warning (e.g. highlighted in red). "
            "This does not block the process and is for informational purposes only."
        ),
    )
    max_reading_value = fields.Integer(
        string="Max Reading",
        tracking=True,
        help=(
            "Maximum value of the meter. "
            "If the entered reading exceeds this value, the system will assume "
            "the meter has rolled over and restart the calculation from 1. "
            "Set to 0 if the meter has no maximum limit."
        ),
    )
    company_ids = fields.Many2many(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    active = fields.Boolean(
        default=True,
        tracking=True,
    )
    update_last_reading = fields.Boolean(
        default=True,
        tracking=True,
        help=("If unchecked, posting an invoice will not update the Last Reading "),
    )

    @api.depends("base_rate", "adjustment_rate")
    def _compute_total_rate(self):
        for rec in self:
            rec.total_rate = rec.base_rate + rec.adjustment_rate

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            name = rec.name
            if rec.code:
                name = f"[{rec.code}] {rec.name}"
            rec.display_name = name
