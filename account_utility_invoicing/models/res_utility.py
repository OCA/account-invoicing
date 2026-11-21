# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ResUtility(models.Model):
    _name = "res.utility"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Utility"
    _rec_names_search = ["code", "name"]
    _check_company_auto = True
    _order = "product_tmpl_id, name"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        index=True,
        tracking=True,
        check_company=True,
    )
    name = fields.Char(
        required=True,
        tracking=True,
        translate=True,
    )
    code = fields.Char(
        tracking=True,
    )
    utility_type_id = fields.Many2one(
        comodel_name="res.utility.type",
        index=True,
        domain="[('company_ids', 'child_of', company_id)]",
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        tracking=True,
        check_company=True,
        string="Customer",
        help=(
            "Customer to be invoiced for this utility. "
            "Invoices generated from this utility will be issued to this customer."
        ),
    )
    last_reading = fields.Float(
        digits="Utility Reading",
        tracking=True,
        help="Last reading of the meter.",
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        compute="_compute_account_id",
        store=True,
        readonly=False,
        check_company=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        required=True,
    )
    total_rate = fields.Float(
        digits="Energy Rate",
        compute="_compute_total_rate",
        store=True,
        help="Total rate is the Utility Type Total Rate * Multiplier.",
    )
    multiplier = fields.Float(
        default=1.0,
        tracking=True,
        help=(
            "Multiplier applied to the Utility Type total rate "
            "when computing the final charge."
        ),
    )
    max_reading_value = fields.Integer(
        string="Max Reading",
        compute="_compute_max_reading_value",
        store=True,
        readonly=False,
        help=(
            "Maximum value of the meter. "
            "If the entered reading exceeds this value, the system will assume "
            "the meter has rolled over and restart the calculation from 1. "
            "Set to 0 if the meter has no maximum limit."
        ),
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    status = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("damage", "Damaged"),
            ("temp", "Temporary"),
            ("cancel", "Cancelled"),
        ],
        default="normal",
        required=True,
        help=(
            "Operational status of the utility. "
            "This status may affect invoicing behavior."
        ),
    )
    is_billable = fields.Boolean(
        compute="_compute_is_billable",
        string="Billable",
        store=True,
        readonly=False,
        help=(
            "Controls whether this utility is billable. "
            "Non-billable utilities will be excluded from invoice generation."
        ),
    )

    @api.depends("status")
    def _compute_is_billable(self):
        """Hooks to allow custom logic for billable status"""
        for rec in self:
            rec.is_billable = rec.status != "cancel"

    @api.depends("utility_type_id", "utility_type_id.total_rate", "multiplier")
    def _compute_total_rate(self):
        for rec in self:
            rec.total_rate = rec.utility_type_id.total_rate * rec.multiplier

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            name = rec.name
            if rec.code:
                name = f"[{rec.code}] {rec.name}"
            rec.display_name = name

    @api.depends("utility_type_id")
    def _compute_max_reading_value(self):
        """default from utility type"""
        for rec in self:
            if rec.utility_type_id:
                rec.max_reading_value = rec.utility_type_id.max_reading_value

    @api.depends("utility_type_id")
    def _compute_account_id(self):
        """default from utility type"""
        for rec in self:
            if rec.utility_type_id:
                rec.account_id = rec.utility_type_id.account_id
