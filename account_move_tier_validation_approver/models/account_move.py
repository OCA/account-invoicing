# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    approver_id = fields.Many2one("res.users", string="Responsible for Approval")

    @api.onchange("partner_id")
    def _onchange_partner_approver_id(self):
        if self.partner_id:
            self.approver_id = self.partner_id.approver_id.id

    def _post(self, soft=True):
        for move in self:
            require_approver_in_vendor_bills = (
                move.company_id.require_approver_in_vendor_bills
            )
            if (
                move.is_purchase_document(include_receipts=True)
                and require_approver_in_vendor_bills
                and not move.approver_id
            ):
                raise UserError(
                    _(
                        "It is mandatory to indicate a Responsible for Approval (in {})"
                    ).format(move.name)
                )
        return super()._post(soft)
