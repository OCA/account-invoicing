# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    ar_ap_account_id = fields.Many2one(
        comodel_name="account.account", check_company=True
    )
    ar_ap_account_domain = fields.Binary(compute="_compute_ar_ap_account_domain")

    def _compute_ar_ap_account_domain(self):
        for record in self:
            if record.type not in ["sale", "purchase"]:
                record.ar_ap_account_domain = []
                continue
            account_type = (
                "asset_receivable" if record.type == "sale" else "liability_payable"
            )
            domain = [("account_type", "=", account_type), ("deprecated", "=", False)]
            if record.account_control_ids:
                domain.append(("id", "in", record.account_control_ids.ids))
            record.ar_ap_account_domain = domain
