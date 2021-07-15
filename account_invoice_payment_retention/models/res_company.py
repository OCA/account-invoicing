# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    retention_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Retention Account",
        domain=[("user_type_id.type", "=", "other")],
        help="Retention account used for case payment retention",
    )

    @api.constrains("retention_account_id")
    def _check_retention_account_id(self):
        for rec in self.filtered("retention_account_id"):
            if not rec.retention_account_id.reconcile:
                raise ValidationError(
                    _("Retention account should be set to allow Reconciliation")
                )
