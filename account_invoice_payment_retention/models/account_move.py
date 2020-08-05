# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    require_retention = fields.Boolean(compute="_compute_require_retention")
    has_payment_retention = fields.Boolean(
        string="Has Retention",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=False,
        copy=False,
    )
    retention_percent = fields.Float(
        string="Retention Percent",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    date_due = fields.Datetime(
        string="Due Date", readonly=True, states={"draft": [("readonly", False)]},
    )
    retention_bill_id = fields.Many2one(
        "account.move.line",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('account_id', '=', 'Retention')]",
        string="Retention Bill",
        help="Auto-complete from a past bill / purchase order.",
    )

    def _compute_require_retention(self):
        self.require_retention = self.env.user.has_group(
            "account_invoice_payment_retention.group_enable_retention"
        )

    @api.onchange("partner_id")
    def _onchange_partner_id_in_late_wa(self):
        self.retention_bill_id = False
        self.invoice_line_ids = False
        self.line_ids = False
        domain = []
        if self.partner_id:
            domain = [
                ("partner_id", "=", self.partner_id.id),
                ("account_id", "=", "Retention"),
            ]
            return {"domain": {"retention_bill_id": domain}}

    @api.onchange("retention_bill_id")
    def _onchange_retention_bill(self):
        if self.retention_bill_id:
            for line in self.retention_bill_id:
                copied_vals = line.copy_data()[0]
                copied_vals["move_id"] = self.id
                copied_vals["name"] = "Retention"
                copied_vals["price_unit"] = line.credit
                new_line = self.env["account.move.line"].new(copied_vals)
                new_line.recompute_tax_line = True
            self._onchange_currency()
