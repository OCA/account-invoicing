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
        for invoice in self:
            if invoice.type not in ["out_invoice", "out_refund"]:
                continue
            # Remove previous lines
            invoice.product_move_ids.line_ids.unlink()
            # Remove previous journal entries
            invoice.product_move_ids.with_context(force_delete=True).unlink()
            invoice.invoice_line_ids._create_extra_moves()
        return res
