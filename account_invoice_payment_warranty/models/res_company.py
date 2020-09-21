# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    warranty_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Warranty Account",
        domain=[("user_type_id.type", "=", "other")],
        help="Warranty account used for case payment warranty",
    )

    @api.constrains("warranty_account_id")
    def _check_warranty_account_id(self):
        for rec in self.filtered("warranty_account_id"):
            if not rec.warranty_account_id.reconcile:
                raise ValidationError(
                    _("Warranty account should be set to allow Reconciliation")
                )
