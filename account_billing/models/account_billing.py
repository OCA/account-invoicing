# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


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
        states={"draft": [("readonly", False)]},
        default=fields.Date.context_today,
        help="Effective date for accounting entries",
        tracking=True,
    )
    threshold_date = fields.Date(
        readonly=True,
        states={"draft": [("readonly", False)]},
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
        states={"draft": [("readonly", False)]},
        help="Notes",
    )
    bill_type = fields.Selection(
        selection=[("out_invoice", "Customer Invoice"), ("in_invoice", "Vendor Bill")],
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self._context.get("bill_type", False),
        help="Type of invoice",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Currency",
    )
    billing_line_ids = fields.One2many(
        comodel_name="account.billing.line",
        inverse_name="billing_id",
        string="Bill Lines",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    threshold_date_type = fields.Selection(
        selection=[("invoice_date_due", "Due Date"), ("invoice_date", "Invoice Date")],
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="invoice_date_due",
        help="All invoices with date (threshold date type) before and equal to "
        "threshold date will be listed in billing lines",
    )
    payment_paid_all = fields.Boolean(
        compute="_compute_payment_paid_all",
        store=True,
    )

    @api.depends("billing_line_ids.payment_state")
    def _compute_payment_paid_all(self):
        for rec in self:
            if not rec.billing_line_ids:
                rec.payment_paid_all = False
                continue
            rec.payment_paid_all = all(
                line.payment_state == "paid" for line in rec.billing_line_ids
            )

    def _get_moves(self, date=False, types=False):
        moves = self.env["account.move"].search(
            [
                ("partner_id", "=", self.partner_id.id),
                ("state", "=", "posted"),
                ("payment_state", "!=", "paid"),
                ("currency_id", "=", self.currency_id.id),
                ("date", "<=", self.threshold_date),
                ("move_type", "in", types),
            ]
        )
        return moves

    def _compute_invoice_related_count(self):
        self.invoice_related_count = len(self.billing_line_ids)

    def name_get(self):
        result = [(billing.id, (billing.name or "Draft")) for billing in self]
        return result

    def validate_billing(self):
        for rec in self:
            if not rec.billing_line_ids:
                raise UserError(_("You need to add a line before validate."))
            date_type = dict(self._fields["threshold_date_type"].selection).get(
                self.threshold_date_type
            )
            if any(
                rec.threshold_date
                < (
                    b.threshold_date
                    if self.threshold_date_type == "invoice_date_due"
                    else b.invoice_date
                )
                for b in rec.billing_line_ids
            ):
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
            "view_mode": "tree,form",
            "res_model": "account.move",
            "view_id": False,
            "views": [
                (self.env.ref("account.view_move_tree").id, "tree"),
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


class AccountBillingLine(models.Model):
    _name = "account.billing.line"
    _description = "Billing Line"

    billing_id = fields.Many2one(comodel_name="account.billing")
    move_id = fields.Many2one(
        comodel_name="account.move",
        index=True,
    )
    name = fields.Char(related="move_id.name")
    invoice_date = fields.Date(related="move_id.invoice_date")
    threshold_date = fields.Date(related="move_id.invoice_date_due")
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

    @api.depends("move_id.amount_residual")
    def _compute_amount_residual(self):
        for rec in self:
            sign = -1 if rec.move_id.move_type in ["out_refund", "in_refund"] else 1
            rec.amount_residual = rec.move_id.amount_residual * sign
