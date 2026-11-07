# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountBilling(models.Model):
    _name = "account.billing"
    _description = "Account Billing"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        readonly=True,
        copy=False,
        help="Number of account.billing",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        help="Partner Information",
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
        required=True,
    )
    date = fields.Date(
        string="Billing Date",
        readonly=True,
        default=fields.Date.context_today,
        help="Effective date for accounting entries",
        tracking=True,
    )
    threshold_date = fields.Date(
        readonly=True,
        default=lambda self: fields.Date.context_today(self),
        required=True,
        tracking=True,
        help="All invoices with date (threshold date type) before and equal to "
        "threshold date will be listed in billing lines",
    )
    invoice_related_count = fields.Integer(
        string="# of Invoices",
        compute="_compute_invoice_related_count",
        help="Count invoice in billing",
    )
    state = fields.Selection(
        selection=[("draft", "Draft"), ("cancel", "Cancelled"), ("billed", "Billed")],
        string="Status",
        readonly=True,
        default="draft",
        help="""
            * The 'Draft' status is used when a user create a new billing\n
            * The 'Billed' status is used when user confirmed billing,
                billing number is generated\n
            * The 'Cancelled' status is used when user billing is cancelled
        """,
    )
    narration = fields.Html(
        string="Notes",
        readonly=True,
        help="Notes",
    )
    bill_type = fields.Selection(
        selection=[("out_invoice", "Customer Invoice"), ("in_invoice", "Vendor Bill")],
        readonly=True,
        default=lambda self: self.env.context.get("bill_type", False),
        help="Type of invoice",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        readonly=True,
        help="Currency",
    )
    billing_line_ids = fields.One2many(
        comodel_name="account.billing.line",
        inverse_name="billing_id",
        string="Bill Lines",
        readonly=True,
    )
    threshold_date_type = fields.Selection(
        selection=[("invoice_date_due", "Due Date"), ("invoice_date", "Invoice Date")],
        required=True,
        readonly=True,
        default=lambda self: self._get_default_threshold_date_type(),
        help="All invoices with date (threshold date type) before and equal to "
        "threshold date will be listed in billing lines",
    )
    payment_paid_all = fields.Boolean(
        compute="_compute_payment_paid_all",
        store=True,
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_amount",
        store=True,
    )
    amount_tax = fields.Monetary(
        string="Tax Amount",
        compute="_compute_amount",
        store=True,
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        compute="_compute_amount",
        store=True,
    )
    amount_due = fields.Monetary(
        compute="_compute_amount_due",
        store=True,
    )

    is_sent = fields.Boolean(
        readonly=True,
        copy=False,
        help="It indicates that the billing has been sent by email.",
    )
    sending_data = fields.Json(copy=False)
    is_being_sent = fields.Boolean(compute="_compute_is_being_sent")

    @api.model
    def _get_default_threshold_date_type(self):
        return "invoice_date_due"

    @api.depends("billing_line_ids.payment_state")
    def _compute_payment_paid_all(self):
        for rec in self:
            if not rec.billing_line_ids:
                rec.payment_paid_all = False
                continue
            rec.payment_paid_all = all(
                line.payment_state == "paid" for line in rec.billing_line_ids
            )

    def _get_moves_domain(self, date, types=False):
        return [
            ("company_id", "=", self.company_id.id),
            ("partner_id", "=", self.partner_id.id),
            ("state", "=", "posted"),
            ("payment_state", "!=", "paid"),
            ("currency_id", "=", self.currency_id.id),
            (date, "<=", self.threshold_date),
            ("move_type", "in", types),
        ]

    def _get_moves(self, date, types=False):
        domain = self._get_moves_domain(date, types=types)
        return self.env["account.move"].search(domain)

    @api.depends("sending_data")
    def _compute_is_being_sent(self):
        for billing in self:
            billing.is_being_sent = bool(billing.sending_data)

    @api.depends("billing_line_ids")
    def _compute_invoice_related_count(self):
        for rec in self:
            rec.invoice_related_count = len(rec.billing_line_ids)

    @api.depends("billing_line_ids.amount_residual")
    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = sum(rec.billing_line_ids.mapped("amount_residual"))

    @api.depends(
        "billing_line_ids.move_id.amount_untaxed", "billing_line_ids.move_id.amount_tax"
    )
    def _compute_amount(self):
        for bill in self:
            bill.amount_untaxed = 0.0
            bill.amount_tax = 0.0
            bill.amount_total = 0.0

            for line in bill.billing_line_ids:
                sign = (
                    -1 if line.move_id.move_type in ["out_refund", "in_refund"] else 1
                )
                bill.amount_untaxed += line.move_id.amount_untaxed * sign
                bill.amount_tax += line.move_id.amount_tax * sign

            bill.amount_total = bill.amount_untaxed + bill.amount_tax

    def _compute_display_name(self):
        for billing in self:
            billing.display_name = billing.name or "Draft Billing"

    @api.onchange("threshold_date_type")
    def _onchange_threshold_date_type(self):
        self._sort_billing_lines()

    def _sort_billing_lines(self):
        if not self.billing_line_ids:
            return
        sorted_lines = self.billing_line_ids.sorted(
            key=lambda x: (x.invoice_date or date.min, x.name or "", x.id)
        )
        for idx, line in enumerate(sorted_lines, start=1):
            line.sequence = idx * 10
        self.invalidate_recordset(["billing_line_ids"])

    def validate_billing(self):
        for rec in self:
            if not rec.billing_line_ids:
                raise UserError(self.env._("You need to add a line before validate."))
            date_type = dict(self._fields["threshold_date_type"].selection).get(
                rec.threshold_date_type
            )
            if any(rec.threshold_date < b.invoice_date for b in rec.billing_line_ids):
                raise ValidationError(
                    self.env._(
                        "Threshold Date cannot be later than the %(date_type)s in "
                        "lines",
                        date_type=date_type,
                    )
                )
            # keep the number in case of a billing reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.bill_type == "out_invoice":
                    sequence_code = "account.customer.billing"
                if rec.bill_type == "in_invoice":
                    sequence_code = "account.supplier.billing"
                rec.name = (
                    self.env["ir.sequence"]
                    .with_context(ir_sequence_date=rec.date)
                    .next_by_code(sequence_code)
                )
            rec.write({"state": "billed"})
            rec.message_post(body=self.env._("Billing is billed."))
        return True

    def action_cancel_draft(self):
        for rec in self:
            rec.write({"state": "draft"})
            rec.message_post(body=self.env._("Billing is reset to draft"))
        return True

    def action_cancel(self):
        for rec in self:
            invoice_paid = rec.billing_line_ids.mapped("move_id").filtered(
                lambda m: m.payment_state == "paid"
            )
            if invoice_paid:
                raise ValidationError(self.env._("Invoice paid already."))
            rec.write({"state": "cancel"})
            rec.message_post(
                body=self.env._("Billing %(name)s is cancelled", name=rec.name)
            )
        return True

    def action_register_payment(self):
        return self.mapped("billing_line_ids.move_id").action_register_payment()

    def invoice_relate_billing_tree_view(self):
        self.ensure_one()
        name = (
            self.env._("Invoices")
            if self.bill_type == "out_invoice"
            else self.env._("Bills")
        )
        return {
            "name": name,
            "view_mode": "list,form",
            "res_model": "account.move",
            "view_id": False,
            "views": [
                (self.env.ref("account.view_move_tree").id, "list"),
                (self.env.ref("account.view_move_form").id, "form"),
            ],
            "type": "ir.actions.act_window",
            "domain": [("id", "in", [rec.move_id.id for rec in self.billing_line_ids])],
            "context": {"create": False},
        }

    def _get_billing_line_dict(self, moves):
        billing_line_dict = [
            {
                "billing_id": self.id,
                "move_id": m.id,
                "amount_total": m.amount_total
                * (-1 if m.move_type in ["out_refund", "in_refund"] else 1),
            }
            for m in moves
        ]
        return billing_line_dict

    def compute_lines(self):
        self.ensure_one()
        self.billing_line_ids = False
        types = ["in_invoice", "in_refund"]
        if self.bill_type == "out_invoice":
            types = ["out_invoice", "out_refund"]
        moves = self._get_moves(self.threshold_date_type, types)
        billing_line_dict = self._get_billing_line_dict(moves)
        self.billing_line_ids.create(billing_line_dict)
        self._sort_billing_lines()

    def _get_billing_email_template(self):
        self.ensure_one()
        template = self.company_id.billing_email_template_id or self.env.ref(
            "account_billing.email_template_billing", raise_if_not_found=False
        )
        if not template:
            raise UserError(
                self.env._(
                    "Please configure the Billing Email Template in the settings."
                )
            )
        return template

    def action_billing_send(self):
        if any(billing.state != "billed" for billing in self):
            raise UserError(self.env._("Only validated billings can be sent by email."))
        if any(self.mapped("is_being_sent")):
            raise UserError(self.env._("Some billings are already being sent."))
        if len(self) > 1:
            return self._action_billing_send_batch()
        template = self._get_billing_email_template()
        ctx = dict(
            self.env.context,
            default_model="account.billing",
            default_res_ids=self.ids,
            default_template_id=template.id,
            default_composition_mode="comment",
            default_email_layout_xmlid=(
                "mail.mail_notification_layout_with_responsible_signature"
            ),
            email_notification_allow_footer=True,
            force_email=True,
            mark_billing_as_sent=True,
        )
        return {
            "name": self.env._("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "target": "new",
            "context": ctx,
        }

    def _action_billing_send_batch(self):
        """Queue the billings for the cron, as account does for invoices:
        rendering one PDF per billing does not fit in a single request."""
        for billing in self:
            billing._get_billing_email_template()
        cron = self.env.ref("account_billing.ir_cron_account_billing_send")
        if not cron.sudo().active:
            raise UserError(
                self.env._(
                    "Batch sending of billings is unavailable. Please ask your "
                    "administrator to activate the scheduled action '%s'.",
                    cron.sudo().name,
                )
            )
        self.sending_data = {
            "author_user_id": self.env.user.id,
            "author_partner_id": self.env.user.partner_id.id,
        }
        cron._trigger()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "info",
                "title": self.env._("Sending billings"),
                "message": self.env._("Billings are being sent in the background."),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def _send_billing_email(self):
        self.ensure_one()
        self.with_context(mark_billing_as_sent=True).message_post_with_source(
            self._get_billing_email_template(),
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            email_layout_xmlid=(
                "mail.mail_notification_layout_with_responsible_signature"
            ),
        )

    def message_post(self, **kwargs):
        if self.env.context.get("mark_billing_as_sent"):
            self.filtered(lambda b: not b.is_sent).write({"is_sent": True})
        return super().message_post(**kwargs)

    @api.model
    def _cron_account_billing_send(self, job_count=10):
        domain = [("sending_data", "!=", False)]
        to_process = self.search(
            domain, order="id", limit=job_count
        ).try_lock_for_update()
        if not to_process:
            return
        billings_by_author = to_process.grouped(
            lambda b: b.sending_data["author_user_id"]
        )
        sent = self.browse()
        for author_id, billings in billings_by_author.items():
            author = self.env["res.users"].browse(author_id)
            for billing in billings.filtered(lambda b: b.state == "billed"):
                try:
                    with self.env.cr.savepoint():
                        billing.with_user(author).with_company(
                            billing.company_id
                        )._send_billing_email()
                    sent |= billing
                except Exception:
                    _logger.exception(
                        "Failed to send billing %s by email", billing.display_name
                    )
        to_process.sending_data = False
        for author_id, billings in billings_by_author.items():
            partner = self.env["res.users"].browse(author_id).partner_id
            billings_error = billings - sent
            if billings_error:
                partner._bus_send(
                    *self._get_send_notification(billings_error, is_success=False)
                )
            if billings & sent:
                partner._bus_send(
                    *self._get_send_notification(billings & sent, is_success=True)
                )
        self.env["ir.cron"]._commit_progress(
            len(to_process), remaining=self.search_count(domain)
        )

    def _get_send_notification(self, billings, is_success):
        return [
            "account_notification",
            {
                "type": "success" if is_success else "warning",
                "title": self.env._("Billings sent")
                if is_success
                else self.env._("Billings in error"),
                "message": self.env._("Billings sent successfully.")
                if is_success
                else self.env._("One or more billings couldn't be sent."),
                "action_button": {
                    "name": self.env._("Open"),
                    "action_name": self.env._("Sent billings")
                    if is_success
                    else self.env._("Billings in error"),
                    "model": "account.billing",
                    "res_ids": billings.ids,
                },
            },
        ]


class AccountBillingLine(models.Model):
    _name = "account.billing.line"
    _description = "Billing Line"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    billing_id = fields.Many2one(comodel_name="account.billing")
    move_id = fields.Many2one(
        comodel_name="account.move",
        index=True,
    )
    name = fields.Char(related="move_id.name")
    invoice_date = fields.Date(compute="_compute_invoice_date")
    origin = fields.Char(related="move_id.invoice_origin")
    currency_id = fields.Many2one(related="move_id.currency_id")
    amount_total = fields.Monetary(
        string="Total",
        readonly=True,
    )
    amount_residual = fields.Monetary(
        compute="_compute_amount_residual",
        store=True,
        string="Amount Due",
    )
    state = fields.Selection(related="move_id.state")
    payment_state = fields.Selection(related="move_id.payment_state")

    @api.depends(
        "billing_id.threshold_date_type",
        "move_id.invoice_date",
        "move_id.invoice_date_due",
    )
    def _compute_invoice_date(self):
        for line in self:
            if line.billing_id.threshold_date_type == "invoice_date_due":
                line.invoice_date = line.move_id.invoice_date_due
                continue
            line.invoice_date = line.move_id.invoice_date

    @api.depends("move_id.amount_residual")
    def _compute_amount_residual(self):
        for rec in self:
            sign = -1 if rec.move_id.move_type in ["out_refund", "in_refund"] else 1
            rec.amount_residual = rec.move_id.amount_residual * sign
