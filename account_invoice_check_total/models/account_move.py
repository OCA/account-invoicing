# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round

GROUP_AICT = "account_invoice_check_total.group_supplier_inv_check_total"


class AccountMove(models.Model):
    _inherit = "account.move"

    check_total = fields.Monetary(
        string="Verification Total",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    check_total_display_difference = fields.Monetary(
        string="Total Difference", compute="_compute_total_display_difference"
    )

    @api.depends("check_total", "amount_total")
    def _compute_total_display_difference(self):
        for invoice in self:
            invoice.check_total_display_difference = float_round(
                invoice.check_total - invoice.amount_total,
                precision_rounding=invoice.currency_id.rounding,
            )

    def action_post(self):
        for inv in self:
            if (
                self.env.user.has_group(GROUP_AICT)
                and inv.move_type in ("in_invoice", "in_refund")
                and float_compare(
                    inv.check_total,
                    inv.amount_total,
                    precision_rounding=inv.currency_id.rounding,
                )
                != 0
            ):
                raise ValidationError(
                    _(
                        "Please verify the price of the invoice!\n"
                        "The total amount (%s) does not match "
                        "the Verification Total amount (%s)!\n"
                        "There is a difference of %s"
                    )
                    % (
                        inv.amount_total,
                        inv.check_total,
                        inv.check_total_display_difference,
                    )
                )
        return super().action_post()

    @api.model
    def _reverse_move_vals(self, default_values, cancel=True):
        vals = super()._reverse_move_vals(default_values, cancel)
        if self.move_type in ["in_invoice", "in_refund"]:
            vals["check_total"] = self.check_total
        return vals
