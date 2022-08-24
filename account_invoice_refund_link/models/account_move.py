# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2022 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    refund_invoice_ids = fields.One2many(
        "account.move", "reversed_entry_id", string="Refund Invoices", readonly=True
    )

    @api.model
    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super()._reverse_move_vals(default_values, cancel)
        if self.env.context.get("link_origin_line", False) and move_vals["type"] in (
            "out_refund",
            "in_refund",
        ):
            refund_lines_vals = [
                x[2]
                for x in move_vals.get("line_ids", [])
                if not x[2].get("exclude_from_invoice_tab", True)
            ]
            for i, line in enumerate(self.invoice_line_ids):
                refund_lines_vals[i]["origin_line_id"] = line.id
        return move_vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    origin_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Original invoice line",
        help="Original invoice line to which this refund invoice line "
        "is referred to",
        index=True,
        copy=False,
    )
    refund_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="origin_line_id",
        string="Refund invoice lines",
        help="Refund invoice lines created from this invoice line",
        copy=False,
    )
