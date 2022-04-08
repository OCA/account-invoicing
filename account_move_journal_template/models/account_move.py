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

    def action_post(self):
        res = super().action_post()
        if self.type != "out_invoice":
            return res
        # Remove previous lines
        self.journal_entry_ids.line_ids.unlink()
        account_auto_model = self.env["account.move.journal.template"]
        product_tmpl_ids = self.mapped("invoice_line_ids.product_id.product_tmpl_id")
        all_journals = self.env["account.move"]
        for tmpl in product_tmpl_ids:
            # This is either a singleton, or an empty recordset
            # because of a UNIQUE constraint in product_tmpl_id
            account_auto = account_auto_model.search(
                [("product_tmpl_line_ids.product_tmpl_id", "=", tmpl.id)]
            )
            if not account_auto:
                continue
            quantity_in_invoice_lines = self._get_quantity_in_invoice_line(tmpl)
            for item in account_auto.journal_item_ids:
                journal = self._get_or_create_journal(item)
                self._create_journal_entry_item(
                    quantity_in_invoice_lines, journal, item
                )
                # TODO: revisit this
                # I expected that recordsets will behave like sets
                # This is not the case here: If I do all_journals+=journal,
                # where journal is id 18, then all_journals becomes
                # something like account.move(18,18,18,...)
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
        line_model.create(
            {
                "move_id": journal.id,
                "account_id": item.account_id.id,
                "currency_id": item.currency_id.id,
                "credit": item.credit * quantity,
                "debit": item.debit * quantity,
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
