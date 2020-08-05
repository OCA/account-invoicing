# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    has_payment_retention = fields.Boolean(
        string="Has Payment Retention", default=False, copy=False,
    )
    retention_percent = fields.Float(string="Retention Percent", readonly=True,)

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        active_ids = self._context.get("active_ids") or self._context.get("active_id")
        invoices = (
            self.env["account.move"]
            .browse(active_ids)
            .filtered(lambda move: move.is_invoice(include_receipts=True))
        )
        res.update(
            {
                "has_payment_retention": invoices[0].has_payment_retention,
                "retention_percent": invoices[0].retention_percent,
            }
        )
        return res

    def post(self):
        res = super().post()
        if self.has_payment_retention:
            if self.writeoff_account_id.name != "Retention":
                raise UserError(
                    _(
                        "You have retention, please complete amount {},"
                        "retention amount {} and recorded in the "
                        "account Retention".format(
                            (
                                self.amount
                                - self.amount * (self.retention_percent / 100)
                            ),
                            self.amount * (self.retention_percent / 100),
                        )
                    )
                )
        return res
