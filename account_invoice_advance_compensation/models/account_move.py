# Copyright 2025, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    advance_invoice = fields.Boolean(
        string="Has Advance Payments",
        compute="_compute_advance_invoice",
        help="Indicates whether this invoice has eligible advance payments available",
    )

    @api.depends(
        "partner_id",
        "move_type",
        "state",
        "line_ids.account_id.account_type",
        "line_ids.amount_residual",
    )
    def _compute_advance_invoice(self):
        self.advance_invoice = False
        invoices = self.filtered(lambda m: m.partner_id and m.is_invoice())
        prepayment_account_type = "asset_prepayments"
        for partner in invoices.partner_id:
            partner_invoices = invoices.filtered_domain(
                [("partner_id", "=", partner.id)]
            )
            domain = self._get_advance_domain(partner, prepayment_account_type)
            partner_invoices.advance_invoice = bool(
                self.env["account.move.line"].search(domain, limit=1)
            )

    def _get_advance_domain(self, partner, account_type):
        return [
            ("move_id.state", "=", "posted"),
            ("move_id.payment_state", "=", "paid"),
            ("partner_id", "=", partner.id),
            ("account_id.account_type", "=", account_type),
            ("account_id.reconcile", "=", True),
            ("amount_residual", "!=", 0),
        ]

    def action_open_advance_compensation(self):
        self.ensure_one()
        self._validate_advance_compensation()
        return {
            "name": _("Compensate Advance"),
            "type": "ir.actions.act_window",
            "res_model": "account.invoice.advance.compensation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "account.move",
                "active_id": self.id,
                "active_ids": self.ids,
                "default_move_id": self.id,
                "default_move_type": self.move_type,
            },
        }

    def _validate_advance_compensation(self):
        if not self.partner_id:
            raise ValidationError(
                _("Advance compensation requires an invoice with a partner.")
            )

        if not self.is_invoice(include_receipts=False):
            raise ValidationError(
                _("Advance compensation is only available for invoices and bills.")
            )

        if not self.advance_invoice:
            raise ValidationError(
                _("No open prepayment entries were found for partner '%(partner)s'.")
                % {"partner": self.partner_id.display_name}
            )
