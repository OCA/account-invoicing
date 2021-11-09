# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class GlobalDiscount(models.Model):
    _inherit = "global.discount"
    _check_company_auto = True

    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Account",
        domain="[('user_type_id.type', 'not in', ['receivable', 'payable'])]",
        check_company=True,
    )
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic account",
        check_company=True,
    )

    def _get_global_discount_vals(self, base, account_id=False, **kwargs):
        """Return account as well if passed"""
        res = super()._get_global_discount_vals(base)
        if account_id:
            res.update({"account_id": account_id})
        return res
