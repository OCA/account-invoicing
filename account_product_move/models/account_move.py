# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    product_move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="invoice_move_id",
        help="Extra moves generated for invoice lines that hold "
        "a product connected to an account.product.move record",
    )
    invoice_move_id = fields.Many2one(
        comodel_name="account.move",
        help="Identifier connecting extra moves to the original invoice",
    )

    def button_draft(self):
        res = super().button_draft()
        if self.product_move_ids and self.state == "draft":
            self.product_move_ids.button_draft()
        return res

    def button_cancel(self):
        res = super().button_cancel()
        if self.product_move_ids and self.state == "cancel":
            self.product_move_ids.button_cancel()
        return res

    def action_view_journal_entries(self):
        self.ensure_one()
        return {
            "name": _("Journal Entries"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "in", self.product_move_ids.ids)],
        }

    def post(self):
        res = super().post()
        extra_moves = self.env["account.move"]
        for move in self:
            if move.type not in ["out_invoice", "out_refund"]:
                continue
            # Remove previous lines
            move.product_move_ids.line_ids.unlink()
            # Remove previous journal entries
            move.product_move_ids.with_context(force_delete=True).unlink()
            for invoice_line in move.invoice_line_ids:
                product_move = invoice_line.product_id.product_tmpl_id.journal_tmpl_id
                if not product_move:
                    continue
                for item in product_move.journal_item_ids:
                    extra_move = move._get_or_create_extra_move(item)
                    move._create_journal_entry_item(
                        invoice_line.quantity, extra_move, item
                    )
                    # TODO: revisit this
                    if extra_move in extra_moves:
                        continue
                    extra_moves += extra_move
            for extra_move in extra_moves:
                extra_move.action_post()
            return res

    def _get_or_create_extra_move(self, item):
        move_model = self.env["account.move"]
        vals = {
            "type": "entry",
            "ref": self.name,
            "journal_id": item.journal_id.id,
            "date": self.invoice_date,
            "invoice_move_id": self.id,
        }
        return move_model.search(
            [
                ("type", "=", vals["type"]),
                ("ref", "=", vals["ref"]),
                ("journal_id", "=", vals["journal_id"]),
                ("date", "=", vals["date"]),
                ("invoice_move_id", "=", vals["invoice_move_id"]),
            ],
            limit=1,
        ) or move_model.create(vals)

    def _create_journal_entry_item(self, quantity, journal, item):
        # We need check_move_validity to False
        # because this will always scream.
        # Instead, ensure that created move lines
        # will be valid, in the account.move.journal.template model
        line_model = self.env["account.move.line"].with_context(
            check_move_validity=False
        )
        credit = item.credit if self.type == "out_invoice" else item.debit
        debit = item.debit if self.type == "out_invoice" else item.credit
        line_model.create(
            {
                "move_id": journal.id,
                "account_id": item.account_id.id,
                "currency_id": item.currency_id.id,
                "credit": credit * quantity,
                "debit": debit * quantity,
            }
        )
