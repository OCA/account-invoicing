# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    journal_entry_ids = fields.One2many(
        comodel_name="account.move", inverse_name="journal_entry_id",
    )
    journal_entry_id = fields.Many2one(comodel_name="account.move")

    def button_draft(self):
        res = super().button_draft()
        for move in self:
            if move.type not in ["out_invoice", "out_refund"]:
                continue
            product_tmpl_ids = move.mapped(
                "invoice_line_ids.product_id.product_tmpl_id"
            )
            for tmpl in product_tmpl_ids:
                template = tmpl.journal_tmpl_id
                if not template:
                    continue
                for item in template.journal_item_ids:
                    move._unlink_journal_entry_item(item)
        return res

    def post(self):
        for move in self:
            if move.type not in ["out_invoice", "out_refund"]:
                continue
            product_tmpl_ids = move.mapped(
                "invoice_line_ids.product_id.product_tmpl_id"
            )
            for tmpl in product_tmpl_ids:
                template = tmpl.journal_tmpl_id
                if not template:
                    continue
                quantity_in_invoice_lines = self._get_quantity_in_invoice_line(tmpl)
                for item in template.journal_item_ids:
                    move._create_journal_entry_item(quantity_in_invoice_lines, item)
        res = super().post()
        return res

    def _create_journal_entry_item(self, quantity, item):
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
                "move_id": self.id,
                "account_id": item.account_id.id,
                "currency_id": item.currency_id.id,
                "credit": credit * quantity,
                "debit": debit * quantity,
                "exclude_from_invoice_tab": True,
            }
        )

    def _unlink_journal_entry_item(self, item):
        domain = [
            ("move_id", "=", self.id),
            ("account_id", "=", item.account_id.id),
            ("currency_id", "=", item.currency_id.id),
        ]
        self.env["account.move.line"].search(domain).unlink()

    def _get_journal_entry_items(self, item):
        domain = [
            ("move_id", "=", self.id),
            ("account_id", "=", item.account_id.id),
            ("currency_id", "=", item.currency_id.id),
        ]
        return self.env["account.move.line"].search(domain)

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
