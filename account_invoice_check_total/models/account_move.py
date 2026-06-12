# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.tools.misc import format_amount

GROUP_AICT = "account_invoice_check_total.group_supplier_inv_check_total"
GROUP_AICT_ADJUST = "account_invoice_check_total.group_supplier_inv_adjust_total"


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
    can_create_check_total_adjustment_line = fields.Boolean(
        compute="_compute_can_create_check_total_adjustment_line"
    )

    @api.depends("state", "move_type", "check_total_display_difference")
    def _compute_can_create_check_total_adjustment_line(self):
        has_group = self.env.user.has_group(GROUP_AICT_ADJUST)
        for move in self:
            move.can_create_check_total_adjustment_line = (
                has_group
                and move.state == "draft"
                and move.move_type in ("in_invoice", "in_refund")
                and not float_is_zero(
                    move.check_total_display_difference,
                    precision_rounding=move.currency_id.rounding,
                )
            )

    @api.depends("check_total", "amount_total")
    def _compute_total_display_difference(self):
        for invoice in self:
            invoice.check_total_display_difference = invoice.currency_id.round(
                invoice.check_total - invoice.amount_total
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
                        "The total amount (%(amount_total)s) does not match "
                        "the Verification Total amount (%(check_total)s)!\n"
                        "There is a difference of %(diff)s"
                    )
                    % {
                        "amount_total": format_amount(
                            self.env, inv.amount_total, inv.currency_id
                        ),
                        "check_total": format_amount(
                            self.env, inv.check_total, inv.currency_id
                        ),
                        "diff": format_amount(
                            self.env,
                            inv.check_total_display_difference,
                            inv.currency_id,
                        ),
                    }
                )
        return super().action_post()

    @api.model
    def _reverse_move_vals(self, default_values, cancel=True):
        vals = super()._reverse_move_vals(default_values, cancel)
        if self.move_type in ["in_invoice", "in_refund"]:
            vals["check_total"] = self.check_total
        return vals

    def action_create_check_total_adjustment_line(self):
        self.ensure_one()
        if not self.env.user.has_group(GROUP_AICT_ADJUST):
            raise ValidationError(
                _("You are not allowed to create an adjustment line.")
            )
        if self.state != "draft":
            raise ValidationError(
                _("The adjustment line can only be created on a draft bill.")
            )
        if self.move_type not in ("in_invoice", "in_refund"):
            raise ValidationError(
                _("The adjustment line is only available on vendor bills and refunds.")
            )

        difference = self.check_total_display_difference
        if float_is_zero(
            difference,
            precision_rounding=self.currency_id.rounding,
        ):
            return

        account = self.journal_id.supplier_inv_adjustment_account_id
        if not account:
            raise ValidationError(
                _(
                    "Please configure a Supplier Invoice Adjustment Account on "
                    "the journal."
                )
            )
        self.env["account.move.line"].create(
            {
                "move_id": self.id,
                "name": _("Adjustment for Verification Total"),
                "account_id": account.id,
                "quantity": 1.0,
                "price_unit": difference,
                "display_type": "product",
                "tax_ids": [(6, 0, [])],
            }
        )
