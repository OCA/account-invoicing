# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    approver_id = fields.Many2one("res.users", string="Responsible for Approval")

    @api.onchange("partner_id")
    def _onchange_partner_approver_id(self):
        if self.partner_id:
            self.approver_id = self.partner_id.approver_id.id

    def post(self):
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
                    _("It is mandatory to indicate a Responsible for Approval")
                )
        return super(AccountMove, self).post()
