# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveDebitnote(models.TransientModel):
    """Account Debit Notes"""

    _name = "account.move.debitnote"
    _description = "Account Debit Note"

    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Journal Entry",
        domain=[
            ("state", "=", "posted"),
            ("type", "not in", ("out_invoice", "in_invoice")),
        ],
    )
    reason = fields.Char()
    date = fields.Date(
        string="Debit Note Date", default=fields.Date.context_today, required=True
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal", string="Use Specific Journal"
    )
    filter_debit = fields.Selection(
        selection=[("debit", "Create a draft debit note")],
        string="Debit Method",
        default="debit",
        required=True,
    )
    # computed fields
    residual = fields.Monetary(compute="_compute_from_moves")
    currency_id = fields.Many2one("res.currency", compute="_compute_from_moves")
    move_type = fields.Char(compute="_compute_from_moves")

    @api.model
    def default_get(self, fields):
        res = super(AccountMoveDebitnote, self).default_get(fields)
        move_ids = (
            self.env["account.move"].browse(self.env.context["active_ids"])
            if self.env.context.get("active_model") == "account.move"
            else self.env["account.move"]
        )
        res["filter_debit"] = "debit"
        res["residual"] = len(move_ids) == 1 and move_ids.amount_residual or 0
        res["currency_id"] = (
            len(move_ids.currency_id) == 1 and move_ids.currency_id.id or False
        )
        res["move_type"] = len(move_ids) == 1 and move_ids.type or False
        return res

    @api.depends("move_id")
    def _compute_from_moves(self):
        move_ids = (
            self.env["account.move"].browse(self.env.context["active_ids"])
            if self.env.context.get("active_model") == "account.move"
            else self.move_id
        )
        for record in self:
            record.residual = len(move_ids) == 1 and move_ids.amount_residual or 0
            record.currency_id = (
                len(move_ids.currency_id) == 1 and move_ids.currency_id or False
            )
            record.move_type = len(move_ids) == 1 and move_ids.type or False

    def invoice_debitnote(self):
        moves = (
            self.env["account.move"].browse(self.env.context["active_ids"])
            if self.env.context.get("active_model") == "account.move"
            else self.move_id
        )
        default_values_list = []
        for move in moves:
            if move.debit_move_id:
                raise ValidationError(_("Can not create Debit Note from Debit Note"))
            default_values_list.append(
                {
                    "ref": _("%s, %s") % (move.name, self.reason)
                    if self.reason
                    else _("%s") % (move.name),
                    "date": self.date or move.date,
                    "invoice_date": move.is_invoice(include_receipts=True)
                    and (self.date or move.date)
                    or False,
                    "journal_id": self.journal_id
                    and self.journal_id.id
                    or move.journal_id.id,
                    "invoice_payment_term_id": None,
                    "auto_post": True
                    if self.date > fields.Date.context_today(self)
                    else False,
                }
            )
        new_moves = moves._create_debitnote(default_values_list)
        action = {
            "name": _("Debit Note"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "context": {"debitnote": True},
        }
        if len(new_moves) == 1:
            action.update({"view_mode": "form", "res_id": new_moves.id})
        else:
            action.update(
                {"view_mode": "tree,form", "domain": [("id", "in", new_moves.ids)]}
            )
        return action
