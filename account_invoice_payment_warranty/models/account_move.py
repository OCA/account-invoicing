# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_warranty = fields.Boolean(
        string="Payment Warranty",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Suggested retention amount to be withheld on payment.\n"
        "Note: as a suggestiong, during payment, user can ignore it.",
    )
    is_return = fields.Boolean(
        string="Return",
        readonly=True,
        copy=False,
        help="This field set True when return warranty.",
    )
    warranty_move_ids = fields.Many2many(
        comodel_name="account.move",
        relation="account_invoice_warranty_move_rel",
        column1="invoice_warranty_id",
        column2="move_id",
        string="Return Warranty",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )

    @api.onchange("is_warranty")
    def _onchange_warranty(self):
        self.invoice_line_ids = False

    @api.onchange("partner_id")
    def _onchange_domain_warranty_move_ids(self):
        self.warranty_move_ids = False
        domain = []
        if self.env.user.has_group(
            "account_invoice_payment_warranty.group_payment_warranty"
        ):
            dom = [
                ("parent_state", "=", "posted"),
                ("account_id", "=", self.env.company.warranty_account_id.id),
                ("reconciled", "=", False),
                ("partner_id", "=", self.partner_id.id),
            ]
            move_lines = self.env["account.move.line"].search(dom)
            move_type = (
                self.type == "out_invoice"
                and "in_invoice"
                or (self.type == "in_invoice" and "out_invoice")
                or "entry"
            )
            move_ids = (
                move_lines.mapped("move_id")
                .filtered(
                    lambda l: l.type == move_type
                    and not l.is_return
                    and l.invoice_payment_state == "paid"
                    and l.is_warranty
                )
                .ids
            )
            domain = [("id", "in", move_ids)]
        return {"domain": {"warranty_move_ids": domain}}

    @api.model
    def _move_lines_warranty_moves(self, warranty_moves):
        """ Get move_lines from selected retained moves in list of dict """
        warranty_move_lines = []
        warranty_account = self.env.company.warranty_account_id
        move_lines = warranty_moves.mapped("line_ids").filtered(
            lambda l: l.account_id == warranty_account and not l.reconciled
        )
        for line in move_lines:
            copied_vals = line.copy_data()[0]
            debit = copied_vals["debit"]
            credit = copied_vals["credit"]
            copied_vals["debit"] = credit
            copied_vals["credit"] = debit
            copied_vals["amount_currency"] = False
            copied_vals["currency_id"] = False
            copied_vals["move_id"] = self.id
            copied_vals["price_unit"] = credit + debit
            copied_vals["price_subtotal"] = (
                copied_vals["quantity"] * copied_vals["price_unit"]
            )
            warranty_move_lines.append(copied_vals)
        return warranty_move_lines

    @api.onchange("warranty_move_ids")
    def _onchange_warranty_move_ids(self):
        self.line_ids = False
        if (
            self.warranty_move_ids
            and len(set(self.warranty_move_ids.mapped("type"))) != 1
        ):
            raise UserError(_("You can't select warranty is not same type."))
        if self.warranty_move_ids:
            lines = self._move_lines_warranty_moves(self.warranty_move_ids)
            for line in lines:
                self.env["account.move.line"].new(line)
        self.currency_id = self.env.company.currency_id
        self._recompute_dynamic_lines()

    def button_draft(self):
        res = super().button_draft()
        warranty_moves = self.mapped("warranty_move_ids").filtered(
            lambda l: l.is_return is True
        )
        if warranty_moves:
            warranty_moves.write({"is_return": False})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def default_get(self, default_fields):
        values = super().default_get(default_fields)
        account_id = values.get("account_id", False)
        warranty = self._context.get("is_warranty", False)
        warranty_account = self.env.company.warranty_account_id
        if account_id and warranty:
            values["account_id"] = warranty_account.id
        return values

    def _get_computed_account(self):
        self.ensure_one()
        res = super()._get_computed_account()
        if self.move_id.is_warranty:
            res = self.env.company.warranty_account_id
        return res
