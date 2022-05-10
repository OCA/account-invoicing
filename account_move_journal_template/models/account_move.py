# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    journal_entry_ids = fields.One2many(
        comodel_name="account.move", inverse_name="journal_entry_id",
    )
    journal_entry_id = fields.Many2one(comodel_name="account.move")

    def button_draft(self):
        res = super().button_draft()
        if self.journal_entry_ids:
            self.journal_entry_ids.button_draft()
        return res

    def button_cancel(self):
        res = super().button_cancel()
        if self.journal_entry_ids:
            self.journal_entry_ids.button_cancel()
        return res

    def action_view_journal_entries(self):
        self.ensure_one()
        return {
            "name": _("Journal Entries"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "in", self.journal_entry_ids.ids)],
        }

    def post(self):
        res = super().post()
        all_journals = self.env["account.move"]
        for move in self:
            if move.type not in ["out_invoice", "out_refund"]:
                continue
            # Remove previous lines
            move.journal_entry_ids.line_ids.unlink()
            product_tmpl_ids = move.mapped(
                "invoice_line_ids.product_id.product_tmpl_id"
            )
            for tmpl in product_tmpl_ids:
                template = tmpl.journal_tmpl_id
                if not template:
                    continue
                quantity_in_invoice_lines = self._get_quantity_in_invoice_line(tmpl)
                for item in template.journal_item_ids:
                    journal = move._get_or_create_journal(item)
                    move._create_journal_entry_item(
                        quantity_in_invoice_lines, journal, item
                    )
                    # TODO: revisit this
                    if journal in all_journals:
                        continue
                    all_journals += journal
            for journal in all_journals:
                journal.action_post()
            return res

    def _get_or_create_journal(self, item):
        journal_model = self.env["account.move"]
        vals = {
            "type": "entry",
            "ref": self.name,
            "journal_id": item.journal_id.id,
            "date": self.invoice_date,
            "journal_entry_id": self.id,
        }
        return journal_model.search(
            [
                ("type", "=", vals["type"]),
                ("ref", "=", vals["ref"]),
                ("journal_id", "=", vals["journal_id"]),
                ("date", "=", vals["date"]),
                ("journal_entry_id", "=", vals["journal_entry_id"]),
            ],
            limit=1,
        ) or journal_model.create(vals)

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

    def _get_quantity_in_invoice_line(self, template):
        return sum(
            self.env["account.move.line"]
            .search(
                [
                    ("move_id", "=", self.id),
                    ("product_id.product_tmpl_id", "=", template.id),
                ]
            )
            .mapped("quantity")
        )
