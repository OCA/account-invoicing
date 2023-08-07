# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2014-2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    origin_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Original invoice line",
        help="Original invoice line to which this refund invoice line "
        "is referred to",
        copy=False,
        index=True,
    )
    refund_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="origin_line_id",
        string="Refund invoice lines",
        help="Refund invoice lines created from this invoice line",
        copy=False,
    )

    def copy_data(self, default=None):
        """Link refund lines with the original ones when copying move lines from the
        `_reverse_move_vals` method.
        """
        res = super().copy_data(default=default)
        if self.env.context.get("link_origin_line"):
            for line, values in zip(self, res):
                values["origin_line_id"] = line.id
        return res
