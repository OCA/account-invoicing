# Copyright 2025 360 ERP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    approver_group_id = fields.Many2one(
        "res.groups",
        string="Group responsible for approval",
        compute="_compute_approver_group_id",
        readonly=False,
        store=True,
    )

    @api.depends("partner_id")
    def _compute_approver_group_id(self):
        for rec in self:
            if rec.approver_group_id:
                rec.approver_group_id = rec.approver_group_id
            elif rec.partner_id.approver_group_id:
                rec.approver_group_id = rec.partner_id.approver_group_id
            else:
                rec.approver_id = False

    def _post(self, soft=True):
        for move in self:
            move._check_has_approver()
        return super()._post(soft)

    def _check_has_approver(self):
        """Overload base function to take into account approver group"""
        require_approver_in_vendor_bills = (
            self.company_id.require_approver_in_vendor_bills
        )
        if (
            self.is_purchase_document(include_receipts=True)
            and require_approver_in_vendor_bills
            and not self.approver_id
            and not self.approver_group_id
        ):
            raise UserError(
                self.env._(
                    "It is mandatory to indicate a Responsible for "
                    "Approval individual or group (in {})"
                ).format(self.name)
            )
