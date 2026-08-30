# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import base64
from datetime import date

from odoo import Command, _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


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
        help="Leave this field empty if this route is shared \
            between all companies",
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
        default=lambda self: self._context.get("bill_type", False),
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

    def _compute_invoice_related_count(self):
        self.invoice_related_count = len(self.billing_line_ids)

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

    def name_get(self):
        result = [(billing.id, (billing.name or "Draft")) for billing in self]
        return result

    def validate_billing(self):
        for rec in self:
            if not rec.billing_line_ids:
                raise UserError(_("You need to add a line before validate."))
            date_type = dict(self._fields["threshold_date_type"].selection).get(
                rec.threshold_date_type
            )
            if any(rec.threshold_date < b.invoice_date for b in rec.billing_line_ids):
                raise ValidationError(
                    _("Threshold Date cannot be later than the %s in lines")
                    % (date_type)
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
            rec.message_post(body=_("Billing is billed."))
        return True

    def action_cancel_draft(self):
        for rec in self:
            rec.write({"state": "draft"})
            rec.message_post(body=_("Billing is reset to draft"))
        return True

    def action_cancel(self):
        for rec in self:
            invoice_paid = rec.billing_line_ids.mapped("move_id").filtered(
                lambda m: m.payment_state == "paid"
            )
            if invoice_paid:
                raise ValidationError(_("Invoice paid already."))
            rec.write({"state": "cancel"})
            self.message_post(body=_("Billing %s is cancelled") % rec.name)
        return True

    def action_register_payment(self):
        return self.mapped("billing_line_ids.move_id").action_register_payment()

    def invoice_relate_billing_tree_view(self):
        name = self.bill_type == "out_invoice" and "Invoices" or "Bills"
        return {
            "name": _("%s") % (name),
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
        self.billing_line_ids = False
        types = ["in_invoice", "in_refund"]
        if self.bill_type == "out_invoice":
            types = ["out_invoice", "out_refund"]
        moves = self._get_moves(self.threshold_date_type, types)
        billing_line_dict = self._get_billing_line_dict(moves)
        self.billing_line_ids.create(billing_line_dict)
        self._sort_billing_lines()

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

    def _get_billing_report(self):
        """Report used to render the PDF attached to the billing email.

        Extracted as a hook so other modules can substitute their own
        report without overriding the whole send action.
        """
        return self.env.ref("account_billing.report_account_billing")

    def action_billing_send(self):
        self.ensure_one()
        template = self.company_id.billing_email_template_id or self.env.ref(
            "account_billing.email_template_billing", raise_if_not_found=False
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
        report = self._get_billing_report()
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
