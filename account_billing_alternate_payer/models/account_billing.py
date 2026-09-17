# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountBilling(models.Model):
    _inherit = "account.billing"

    def _get_moves(self, date=False, types=False):
        """Group the invoices by the party that actually pays them.

        The standard billing document collects the invoices whose partner is the
        billing partner. When an invoice has an alternate payer, the receivable
        belongs to that payer, so the invoice must be billed to the payer and not
        to the invoice partner.
        """
        self.ensure_one()
        moves = super()._get_moves(date=date, types=types)
        moves = moves.filtered(
            lambda move: not move.alternate_payer_id
            or move.alternate_payer_id == self.partner_id
        )
        return moves | self._get_alternate_payer_moves(types)

    def _get_alternate_payer_moves(self, types):
        """Invoices issued to other partners but payable by the billing partner."""
        self.ensure_one()
        return self.env["account.move"].search(
            [
                ("alternate_payer_id", "=", self.partner_id.id),
                ("partner_id", "!=", self.partner_id.id),
                ("state", "=", "posted"),
                ("payment_state", "!=", "paid"),
                ("currency_id", "=", self.currency_id.id),
                ("date", "<=", self.threshold_date),
                ("move_type", "in", types),
            ]
        )


class AccountBillingLine(models.Model):
    _inherit = "account.billing.line"

    move_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="move_id.partner_id",
        string="Invoice Partner",
        help="Partner the invoice was issued to, which may differ from the payer.",
    )
