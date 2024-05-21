# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.job import identity_exact


class AccountInvoiceTransmit(models.TransientModel):
    """This wizard will mark as sent the all the selected validated invoices."""

    _name = "account.invoice.transmit"
    _description = "Wizard to send invoices"

    _act_close = {"type": "ir.actions.act_window_close"}

    invoice_ids = fields.Many2many("account.move", readonly=True)

    resend = fields.Boolean(help="Force resending already sent invoices")
    transmit_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_transmit_invoice_ids",
    )

    transmit_undefined_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_transmit_undefined_invoice_ids",
    )
    count_transmit_undefined = fields.Integer(
        "Total undefined",
        compute="_compute_count_transmit_undefined",
    )

    transmit_post_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_transmit_post_invoice_ids",
    )
    count_transmit_post = fields.Integer(
        "Total by post",
        compute="_compute_count_transmit_post",
    )

    transmit_email_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_transmit_email_invoice_ids",
    )
    transmit_email_valid_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_transmit_email_invoice_ids",
    )
    count_transmit_email = fields.Integer(
        "Total by email",
        compute="_compute_count_transmit_email",
    )
    count_transmit_email_missing = fields.Integer(
        "Email address missing",
        compute="_compute_count_transmit_email",
    )

    def default_get(self, fields_list=None):
        result = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])
        if active_model == self.invoice_ids._name:
            result["invoice_ids"] = [fields.Command.set(active_ids)]
        return result

    @api.depends("invoice_ids", "resend")
    def _compute_transmit_invoice_ids(self):
        if self.resend:
            self.transmit_invoice_ids = self.invoice_ids
        else:
            self.transmit_invoice_ids = self.invoice_ids.filtered(
                lambda r: r.is_invoice_to_transmit
            )

    @api.depends("transmit_invoice_ids")
    def _compute_transmit_undefined_invoice_ids(self):
        self.transmit_undefined_invoice_ids = self.transmit_invoice_ids.filtered(
            lambda r: not r.transmit_method_id
        )

    @api.depends("transmit_undefined_invoice_ids")
    def _compute_count_transmit_undefined(self):
        self.count_transmit_undefined = len(self.transmit_undefined_invoice_ids)

    @api.depends("transmit_invoice_ids")
    def _compute_transmit_post_invoice_ids(self):
        self.transmit_post_invoice_ids = self.transmit_invoice_ids.filtered(
            lambda r: r.transmit_method_code == "post"
        )

    @api.depends("transmit_post_invoice_ids")
    def _compute_count_transmit_post(self):
        self.count_transmit_post = len(self.transmit_post_invoice_ids)

    @api.depends("transmit_invoice_ids")
    def _compute_transmit_email_invoice_ids(self):
        invoices = self.transmit_invoice_ids.filtered(
            lambda r: r.transmit_method_code == "mail"
        )
        self.transmit_email_invoice_ids = invoices
        self.transmit_email_valid_invoice_ids = invoices.filtered("partner_id.email")

    @api.depends("transmit_email_invoice_ids")
    def _compute_count_transmit_email(self):
        self.count_transmit_email = len(self.transmit_email_invoice_ids)
        self.count_transmit_email_missing = len(self.transmit_email_invoice_ids) - len(
            self.transmit_email_valid_invoice_ids
        )

    def button_print(self):
        invoices = self.transmit_post_invoice_ids
        if self.resend:
            invoices.filtered("is_move_sent").is_move_sent = False
        description = _("Mass generating invoice reports for sending")
        invoices.with_delay(
            description=description,
            identity_key=identity_exact,
            priority=20,
            channel="root.invoice_transmit.post",
        )._transmit_invoice_by_post()
        self.env.user.notify_info(_("A report will be generated in the background."))
        return self._act_close

    def button_partner_missing_email(self):
        invoices = (
            self.transmit_email_invoice_ids - self.transmit_email_valid_invoice_ids
        )
        action = self.env.ref("base.action_partner_customer_form").read()[0]
        action["domain"] = [("id", "in", invoices.partner_id.ids)]
        return action

    def button_invoices_missing_transmit_method(self):
        invoices = self.transmit_undefined_invoice_ids
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["domain"] = [("id", "in", invoices.ids)]
        return action

    def button_email(self):
        invoices = self.transmit_email_valid_invoice_ids
        if not invoices:
            raise UserError(_("No invoice with valid email to send"))
        if self.resend:
            invoices.filtered("is_move_sent").is_move_sent = False
        description = _("Mass generating invoice emails for sending")
        invoices.with_delay(
            description=description,
            identity_key=identity_exact,
            priority=50,
            channel="root.invoice_transmit.email",
        )._transmit_invoice_by_email()
        self.env.user.notify_info(
            _("Invoices will be sent by email in the background.")
        )
        return self._act_close

    def button_mark_only(self):
        self.invoice_ids.write({"is_move_sent": True})
        for invoice in self.invoice_ids:
            invoice.message_post(body=_("Invoice marked as sent"))
        return self._act_close
