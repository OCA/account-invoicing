# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.move.reversal"

    refund_method = fields.Selection(
        selection_add=[("refund_lines", "Refund specific lines")],
        ondelete={"refund_lines": "cascade"},
    )
    line_ids = fields.Many2many(
        string="Invoice lines to refund",
        comodel_name="account.move.line",
        column1="wiz_id",
        column2="line_id",
        relation="account_invoice_line_refund_rel",
        domain="[('id', 'in', selectable_invoice_lines_ids)]",
    )
    selectable_invoice_lines_ids = fields.Many2many(
        "account.move.line",
    )

    @api.model
    def default_get(self, fields):
        rec = super(AccountInvoiceRefund, self).default_get(fields)
        context = dict(self._context or {})
        active_id = context.get("active_id", False)
        if active_id:
            inv = self.env["account.move"].browse(active_id)
            rec.update(
                {"selectable_invoice_lines_ids": [(6, 0, inv.invoice_line_ids.ids)]}
            )
        return rec

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        if self.refund_method == "refund_lines":
            vals = res.copy()
            vals["line_ids"] = [
                (
                    0,
                    0,
                    li.with_context(include_business_fields=True).copy_data(
                        {"move_id": False, "recompute_tax_line": True}
                    )[0],
                )
                for li in self.line_ids
            ]
            move = self.env["account.move"].new(vals)
            lines = []
            for line in move._move_autocomplete_invoice_lines_values()["line_ids"]:
                if line[0] != 0:
                    continue
                for field_name, field_obj in self.env[
                    "account.move.line"
                ]._fields.items():
                    if (
                        isinstance(field_obj, fields.Boolean)
                        and field_obj.store
                        and field_name not in line[2]
                    ):
                        line[2][field_name] = False
                lines.append(
                    (
                        line[0],
                        line[1],
                        self.env["account.move.line"]._add_missing_default_values(
                            line[2]
                        ),
                    )
                )
            res["line_ids"] = lines
        return res

    def reverse_moves(self):
        # We can uncheck the move, as it is checked by default at the end
        return super(
            AccountInvoiceRefund,
            self.with_context(
                check_move_validity=False,
            ),
        ).reverse_moves()
