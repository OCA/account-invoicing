# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


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

    def action_billing_send(self):
        self.ensure_one()
        template = self.company_id.billing_email_template_id or self.env.ref(
            "account_billing_portal.email_template_billing", raise_if_not_found=False
        )
        if not template:
            raise UserError(
                _("Please configure the Billing Email Template in the settings.")
            )
        compose_form = self.env.ref(
            "mail.email_compose_message_wizard_form", raise_if_not_found=False
        )
        compose_form_id = compose_form.id if compose_form else False
        ctx = dict(self.env.context or {})
        email_xml_id = "mail.mail_notification_layout_with_responsible_signature"
        ctx.update(
            {
                "default_model": "account.billing",
                "default_res_id": self.id,
                "default_template_id": template.id,
                "default_composition_mode": "comment",
                "default_email_layout_xmlid": email_xml_id,
                "force_email": True,
            }
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

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
