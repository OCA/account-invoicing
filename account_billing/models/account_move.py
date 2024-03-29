# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    billing_ids = fields.Many2many(
        comodel_name="account.billing",
        string="Billings",
        compute="_compute_billing_ids",
        help="Relationship between invoice and billing",
    )

    def _compute_billing_ids(self):
        bl_obj = self.env["account.billing.line"]
        for rec in self:
            billing_lines = bl_obj.search([("move_id", "=", rec.id)])
            rec.billing_ids = billing_lines.mapped("billing_id")

    def _create_billing(self, partner):
        billing = self.env["account.billing"].create(
            {
                "partner_id": partner.id,
                "bill_type": list(set(self.mapped("move_type")))[0],
                "billing_line_ids": [
                    Command.create(
                        {
                            "move_id": m.id,
                            "amount_total": m.amount_total
                            * (-1 if m.move_type in ["out_refund", "in_refund"] else 1),
                            "amount_residual": m.amount_residual
                            * (-1 if m.move_type in ["out_refund", "in_refund"] else 1),
                        }
                    )
                    for m in self
                ],
            }
        )
        return billing

    def action_create_billing(self):
        partner = self.mapped("partner_id")
        currency_ids = self.mapped("currency_id")
        if len(partner) > 1:
            raise UserError(_("Please select invoices with same partner"))

        if len(currency_ids) > 1:
            raise UserError(_("Please select invoices with same currency"))

        if any(move.state != "posted" or move.payment_state == "paid" for move in self):
            raise UserError(
                _(
                    "Billing cannot be processed because "
                    "some invoices are not in the 'Posted' or 'Paid' state already."
                )
            )

        billing = self._create_billing(partner)

        action = {
            "name": _("Billing"),
            "type": "ir.actions.act_window",
            "res_model": "account.billing",
            "context": {"create": False},
        }
        if len(billing) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": billing.id,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form",
                    "domain": [("id", "in", billing.ids)],
                }
            )
        return action
