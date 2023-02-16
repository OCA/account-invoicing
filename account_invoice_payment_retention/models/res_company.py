# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    retention_account_id = fields.Many2one(
        comodel_name="account.account",
        domain=[("user_type_id.type", "=", "other")],
        help="Retention account used for case payment retention",
    )
    retention_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        domain=[("user_type_id.type", "=", "other")],
        help="Retention account used for case payment retention",
    )
    retention_method = fields.Selection(
        selection=[("untax", "Untaxed Amount"), ("total", "Total")],
        default="untax",
        help="Method for computing the retention\n"
        "- Untaxed Amount: The retention compute from the untaxed amount\n"
        "- Total: The retention compute from the total amount",
    )

    @api.constrains("retention_account_id")
    def _check_retention_account_id(self):
        for rec in self.filtered("retention_account_id"):
            if not rec.retention_account_id.reconcile:
                raise ValidationError(
                    _("Retention payable account should be set to allow Reconciliation")
                )

    @api.constrains("retention_receivable_account_id")
    def _check_retention_receivable_account_id(self):
        for rec in self.filtered("retention_receivable_account_id"):
            if not rec.retention_receivable_account_id.reconcile:
                raise ValidationError(
                    _(
                        "Retention receivable account should be set to allow Reconciliation"
                    )
                )
