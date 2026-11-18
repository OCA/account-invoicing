# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBilling(models.Model):
    _inherit = ["account.billing", "portal.mixin"]
    _name = "account.billing"

    def _compute_access_url(self):
        super()._compute_access_url()
        for billing in self:
            billing.access_url = f"/my/billings/{billing.id}"
        return

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.name

    def _get_billing_report(self):
        # Use the portal report (if configured) for the billing email
        # attachment as well, so it matches the report shown in the portal.
        return self.company_id.billing_portal_report or super()._get_billing_report()

    def preview_billing(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": self.get_portal_url(),
        }

    def validate_billing(self):
        res = super().validate_billing()
        for rec in self.filtered(lambda x: x.state == "billed"):
            if rec.partner_id not in rec.message_partner_ids:
                rec.message_subscribe([rec.partner_id.id])
        return res
