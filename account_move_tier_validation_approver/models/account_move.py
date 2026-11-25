# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    approver_id = fields.Many2one(
        "res.users",
        string="Responsible for Approval",
        compute="_compute_approver_id",
        readonly=False,
        store=True,
    )
    is_approver_id_readonly = fields.Boolean(
        compute="_compute_is_approver_id_readonly",
        help="technical field to allow complex readonly attribute "
        "logic for the approver_id field on the views",
    )

    @api.depends("review_ids", "state")
    def _compute_is_approver_id_readonly(self):
        can_edit_account_move_tier_validation_approver = self.env.user.has_group(
            "account_move_tier_validation_approver."
            "group_can_edit_account_move_tier_validation_approver"
        )
        for record in self:
            record.is_approver_id_readonly = (
                not can_edit_account_move_tier_validation_approver
                or record.review_ids
                or record.state != "draft"
            )

    @api.depends("partner_id")
    def _compute_approver_id(self):
        for rec in self:
            if rec.approver_id:
                # assign a value in any case
                rec.approver_id = rec.approver_id
            elif rec.partner_id.approver_id:
                rec.approver_id = rec.partner_id.approver_id
            else:
                rec.approver_id = False

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
                    self.env._(
                        "It is mandatory to indicate a Responsible for Approval (in {})"
                    ).format(move.name)
                )
        return super()._post(soft)
