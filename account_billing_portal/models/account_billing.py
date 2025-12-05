# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import Command, _, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


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

    def _get_eval_context(self):
        """Get evaluation context for safe_eval expressions."""
        return {
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "timezone": tools.safe_eval.pytz.timezone,
            "context_today": lambda: fields.Date.context_today(self),
            "object": self,
        }

    def action_billing_send(self):
        self.ensure_one()
        template = self.company_id.billing_email_template_id or self.env.ref(
            "account_billing_portal.email_template_billing"
        )
        if not template:
            raise UserError(
                _("Please configure the Billing Email Template in the settings.")
            )
        try:
            compose_form_id = self.env["ir.model.data"]._xmlid_lookup(
                "mail.email_compose_message_wizard_form"
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        report = self.company_id.billing_portal_report or self.env.ref(
            "account_billing.report_account_billing"
        )
        if not report:
            raise UserError(
                _("Please configure the Billing Portal Report in the settings.")
            )
        pdf_content, _type = report._render_qweb_pdf(report.id, self.ids)
        if report.print_report_name:
            eval_context = self._get_eval_context()
            attachment_name = safe_eval(report.print_report_name, eval_context)
        else:
            attachment_name = self.display_name if self.display_name else "BILLING"
        if not attachment_name.endswith(".pdf"):
            attachment_name = f"{attachment_name}.pdf"
        attach = self.env["ir.attachment"].create(
            {
                "name": attachment_name,
                "type": "binary",
                "datas": base64.b64encode(pdf_content),
                "mimetype": "application/pdf",
                "res_model": "account.billing",
                "res_id": self.id,
            }
        )
        email_xml_id = "mail.mail_notification_layout_with_responsible_signature"
        ctx.update(
            {
                "default_model": "account.billing",
                "default_res_ids": self.ids,
                "default_template_id": template.id,
                "default_composition_mode": "comment",
                "default_email_layout_xmlid": email_xml_id,
                "default_attachment_ids": [Command.set([attach.id])],
                "email_notification_allow_footer": True,
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
