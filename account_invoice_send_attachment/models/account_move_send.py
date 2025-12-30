# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_invoice_extra_attachments(self, move):
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", move.id),
                ("res_model", "=", move._name),
            ]
        )
        return super()._get_invoice_extra_attachments(move) + attachments
