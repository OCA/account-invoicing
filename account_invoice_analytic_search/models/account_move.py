# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_analytic_account_depends(self):
        depends = ["invoice_line_ids"]
        line_model = self.env["account.move.line"]
        if "analytic_distribution" in line_model._fields:
            depends.append("invoice_line_ids.analytic_distribution")
        if "analytic_account_id" in line_model._fields:
            depends.append("invoice_line_ids.analytic_account_id")
        return depends

    @api.depends(lambda self: self._get_analytic_account_depends())
    def _compute_analytic_accounts(self):
        analytic_line_model = self.env["account.move.line"]
        has_legacy = "analytic_account_id" in analytic_line_model._fields
        has_distribution = "analytic_distribution" in analytic_line_model._fields
        AnalyticAccount = self.env["account.analytic.account"]
        for move in self:
            account_ids = set()
            if has_legacy:
                account_ids.update(
                    move.mapped("invoice_line_ids.analytic_account_id").ids
                )
            if has_distribution:
                for line in move.invoice_line_ids:
                    account_ids.update(self._extract_distribution_account_ids(line))
            move.analytic_account_ids = AnalyticAccount.browse(list(account_ids))

    @api.model
    def _extract_distribution_account_ids(self, line):
        account_ids = set()
        distribution = line.analytic_distribution
        if isinstance(distribution, str):
            try:
                distribution = json.loads(distribution)
            except ValueError:
                distribution = {}
        if not isinstance(distribution, dict):
            return account_ids
        for key, data in distribution.items():
            if isinstance(data, dict):
                account_id = data.get("account_id") or data.get("analytic_account_id")
                if account_id:
                    account_ids.add(int(account_id))
                    continue
            key_str = str(key)
            if not key_str:
                continue
            key_token = key_str.replace(":", "-").split("-")[0]
            if key_token.isdigit():
                account_ids.add(int(key_token))
        return account_ids

    analytic_account_ids = fields.Many2many(
        comodel_name="account.analytic.account",
        compute="_compute_analytic_accounts",
        store=True,
        string="Analytic Accounts",
        readonly=True,
    )
