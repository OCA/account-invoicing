# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    approver_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible for Approval",
        track_visibility="onchange",
    )

    @api.onchange("partner_id")
    def _onchange_partner_approver_id(self):
        if self.partner_id:
            self.approver_id = self.partner_id.approver_id.id

    @api.model
    def get_purchase_types(self, include_receipts=False):
        return ['in_invoice', 'in_refund'] + (include_receipts and ['in_receipt'] or [])

    def is_purchase_document(self, include_receipts=False):
        return self.type in self.get_purchase_types(include_receipts)

    def action_invoice_open(self):
        for invoice in self:
            require_approver_in_vendor_bills = (
                invoice.company_id.require_approver_in_vendor_bills
            )
            if (
                invoice.is_purchase_document(include_receipts=True)
                and require_approver_in_vendor_bills
                and not invoice.approver_id
            ):
                raise UserError(
                    _("It is mandatory to indicate a Responsible for Approval")
                )
        return super(AccountInvoice, self).action_invoice_open()
