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
        rec = super().default_get(fields)
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
                        {"move_id": False}
                    )[0],
                )
                for li in self.line_ids
            ]
            reversal_inv = self.env["account.move"].new(vals)
            lines = []
            for line in reversal_inv.line_ids:
                dict_line = line._convert_to_write(line._cache)
                lines.append((0, 0, dict_line))
            res["line_ids"] = lines
        return res
