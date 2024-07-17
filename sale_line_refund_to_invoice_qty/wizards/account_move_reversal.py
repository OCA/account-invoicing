# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    sale_qty_to_reinvoice = fields.Boolean(
        string="This credit note will be reinvoiced",
        help="Leave it marked if you will reinvoice the same sale order line "
        "(standard behaviour)",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        company = (
            self.env["res.company"].browse(res.get("company_id"))
            if res.get("company_id")
            else self.env.company
        )
        res["sale_qty_to_reinvoice"] = company.reinvoice_credit_note_default
        return res

    def reverse_moves(self):
        return super(
            AccountMoveReversal,
            self.with_context(sale_qty_to_reinvoice=self.sale_qty_to_reinvoice),
        ).reverse_moves()
