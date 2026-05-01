# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountUtility(models.Model):
    _name = "account.utility"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True
    _order = "name desc"
    _description = "Account Utility"

    name = fields.Char(
        default="/",
        required=True,
        readonly=True,
        copy=False,
        help="Number of utility document",
    )
    date_invoice = fields.Date(
        string="Invoice Date",
        default=fields.Date.context_today,
    )
    date_due = fields.Date(
        string="Due Date",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        check_company=True,
        domain="[('type', '=', 'sale')]",
    )
    utility_type_ids = fields.Many2many(
        comodel_name="res.utility.type",
        domain="[('company_ids', 'child_of', company_id)]",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        check_company=True,
        string="Customer",
    )
    utility_line_ids = fields.One2many(
        comodel_name="account.utility.line",
        inverse_name="account_utility_id",
        string="Utility Lines",
    )
    invoice_count = fields.Integer(
        compute="_compute_invoice_count",
    )
    amount_total = fields.Monetary(
        string="Total", store=True, compute="_compute_amounts", tracking=4
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("done", "Invoiced"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if not res.get("journal_id"):
            res["journal_id"] = self.env.company.journal_account_utility_id.id
        return res

    @api.depends("utility_line_ids.move_id")
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.utility_line_ids.mapped("move_id"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("account.utility")
        return super().create(vals_list)

    def action_create_invoice(self):
        self.ensure_one()
        self._create_invoices()
        self.write({"state": "done"})
        return self.action_view_invoice()

    def button_confirm(self):
        for rec in self:
            if not rec.utility_line_ids:
                raise ValidationError(self.env._("Utility Lines cannot be empty!"))
            # Due date must greater than or equal to invoice date
            if rec.date_due < rec.date_invoice:
                raise ValidationError(
                    self.env._("Due date must greater than or equal to invoice date.")
                )
        return self.write({"state": "confirm"})

    def button_draft(self):
        return self.write({"state": "draft"})

    def button_cancel(self):
        return self.write({"state": "cancel"})

    def action_view_invoice(self):
        result = {
            "name": self.env._("Invoices"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", self.utility_line_ids.mapped("move_id").ids)],
            "context": {"create": False, "default_move_type": "out_invoice"},
        }
        return result

    def _prepare_invoice_dict(self, partner_id):
        invoice_dict = {
            "move_type": "out_invoice",
            "is_utility": True,
            "partner_id": partner_id,
            "ref": self.name,
            "invoice_date": self.date_invoice,
            "invoice_date_due": self.date_due,
            "journal_id": self.journal_id.id,
            "company_id": self.company_id.id,
        }
        return invoice_dict

    def _create_invoices(self):
        self.ensure_one()
        Invoice = self.env["account.move"]
        # Group lines by partner_id
        grouped_lines = self.utility_line_ids.filtered(
            lambda line: line.amount_subtotal
        ).grouped(lambda line: line.partner_id.id)

        if not grouped_lines:
            return

        invoices_vals = []
        partner_to_lines = {}
        for partner_id, lines in grouped_lines.items():
            invoice_dict = self._prepare_invoice_dict(partner_id)
            invoice_dict["invoice_line_ids"] = [
                Command.create(line._prepare_invoice_line_dict()) for line in lines
            ]
            invoices_vals.append(invoice_dict)
            partner_to_lines[partner_id] = lines

        invoices = Invoice.create(invoices_vals)

        # Add move_id in each line utility
        for invoice in invoices:
            lines = partner_to_lines.get(invoice.partner_id.id, [])
            lines.write({"move_id": invoice.id})

    def _get_domain_search(self):
        domain = [
            ("company_id", "=", self.company_id.id),
            ("is_billable", "=", True),
        ]

        # Filter by utility type
        uti_type = self.utility_type_ids
        if not uti_type:
            uti_type = self.env["res.utility.type"].search([])
        domain.append(("utility_type_id", "in", uti_type.ids))
        # Filter by partner
        partner_ids = self.partner_ids
        if partner_ids:
            domain.append(("partner_id", "in", partner_ids.ids))
        return domain

    def _get_utility_line_dict(self, utility_ids):
        return [
            Command.create(
                {
                    "utility_id": utility.id,
                    "prev_unit": utility.last_reading,
                    "curr_unit": utility.last_reading,
                }
            )
            for utility in utility_ids
        ]

    def retrieve_product_line(self):
        self.utility_line_ids = False
        domain_search = self._get_domain_search()
        utility_ids = self.env["res.utility"].search(domain_search)
        line_dict = self._get_utility_line_dict(utility_ids)
        return self.write({"utility_line_ids": line_dict})

    @api.depends("utility_line_ids.amount_subtotal")
    def _compute_amounts(self):
        for rec in self:
            subtotal = sum(rec.utility_line_ids.mapped("amount_subtotal"))
            rec.amount_total = subtotal


class AccountUtilityLine(models.Model):
    _name = "account.utility.line"
    _description = "Account Utility Lines"
    _rec_name = "utility_id"

    account_utility_id = fields.Many2one(
        comodel_name="account.utility",
        index=True,
        required=True,
        ondelete="cascade",
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        ondelete="set null",
        readonly=True,
    )
    utility_id = fields.Many2one(
        comodel_name="res.utility",
        required=True,
        index=True,
    )
    utility_type_id = fields.Many2one(
        comodel_name="res.utility.type",
        related="utility_id.utility_type_id",
        store=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        related="utility_id.product_tmpl_id",
        store=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="utility_id.partner_id",
        store=True,
    )
    flat_rate = fields.Float()
    prev_unit = fields.Float(
        string="Prev. Unit",
        related="utility_id.last_reading",
        digits="Utility Reading",
        store=True,
    )
    curr_unit = fields.Float(
        string="Curr. Unit",
        digits="Utility Reading",
    )
    total_unit = fields.Float(
        compute="_compute_all_amount",
        digits="Utility Reading",
        store=True,
    )
    amount_subtotal = fields.Float(
        compute="_compute_all_amount",
        store=True,
    )
    is_alert_threshold = fields.Boolean(
        compute="_compute_is_alert_threshold",
        store=True,
        default=False,
    )
    total_rate = fields.Float(related="utility_id.total_rate", store=True)
    multiplier = fields.Float(related="utility_id.multiplier", store=True)

    _sql_constraints = [
        (
            "check_positive_units",
            "CHECK(flat_rate >= 0 "
            "AND prev_unit >= 0 "
            "AND curr_unit >= 0 "
            "AND total_unit >= 0)",
            "Negative amount is not allowed",
        )
    ]

    @api.depends("flat_rate", "prev_unit", "curr_unit", "utility_id.max_reading_value")
    def _compute_all_amount(self):
        for rec in self:
            # Clear curr_unit if flat_rate is set
            if rec.flat_rate:
                rec.curr_unit = rec.prev_unit
                rec.total_unit = 0.0
                rec.amount_subtotal = rec.flat_rate
            else:
                if rec.utility_id.max_reading_value and rec.curr_unit < rec.prev_unit:
                    total_unit = (
                        (rec.utility_id.max_reading_value - rec.prev_unit)
                        + rec.curr_unit
                        + 1
                    )
                else:
                    total_unit = rec.curr_unit - rec.prev_unit
                rec.total_unit = total_unit
                rec.amount_subtotal = total_unit * rec.utility_id.total_rate

    @api.depends("total_unit", "utility_type_id.alert_threshold")
    def _compute_is_alert_threshold(self):
        precision = self.env["decimal.precision"].precision_get("Utility Reading")
        for line in self:
            line.is_alert_threshold = False
            alert_threshold = line.utility_type_id.alert_threshold
            if not alert_threshold or not line.prev_unit:
                continue
            percent_curr = (line.total_unit * 100) / line.prev_unit
            if (
                float_compare(percent_curr, alert_threshold, precision_digits=precision)
                == 1
            ):
                line.is_alert_threshold = True

    def _prepare_invoice_line_dict(self):
        self.ensure_one()
        account_id = self.utility_id.account_id or self.utility_type_id.account_id
        return {
            "name": self.account_utility_id.name,
            "account_id": account_id.id,
            "curr_unit": self.curr_unit,
            "prev_unit": self.prev_unit,
            "quantity": 1 if self.flat_rate else self.total_unit,
            "price_unit": self.flat_rate or self.utility_id.total_rate,
            "utility_line_id": self.id,
        }
