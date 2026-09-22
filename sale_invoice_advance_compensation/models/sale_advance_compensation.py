# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleAdvanceCompensation(models.Model):
    _name = "sale.advance.compensation"
    _description = "Sale Advance Compensation"
    _order = "sale_order_id, id"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    payment_term_line_id = fields.Many2one(
        comodel_name="account.payment.term.line",
        string="Payment Term Line",
        required=True,
        ondelete="restrict",
        index=True,
        domain="[('is_advance', '=', True)]",
    )
    advance_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Advance Line",
        index=True,
        domain="[('account_id.account_type', '=', 'asset_prepayments'), "
        "('account_id.reconcile', '=', True), ('move_id.state', '=', 'posted')]",
        copy=False,
    )
    amount = fields.Monetary(
        required=True,
        currency_field="currency_id",
    )
    applied_amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    remaining_amount = fields.Monetary(
        compute="_compute_remaining_amount",
        currency_field="currency_id",
    )
    available_amount = fields.Monetary(
        compute="_compute_available_amount",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        index=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("reserved", "Reserved"),
            ("invoiced", "Invoiced"),
            ("applied", "Applied"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        copy=False,
        index=True,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        copy=False,
        index=True,
    )
    advance_invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Advance Invoice",
        copy=False,
        readonly=True,
        index=True,
    )
    invoice_ids = fields.Many2many(
        comodel_name="account.move",
        relation="sale_advance_compensation_invoice_rel",
        column1="compensation_id",
        column2="invoice_id",
        string="Invoices",
        copy=False,
    )
    compensation_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Compensation Move",
        copy=False,
        readonly=True,
    )
    compensation_move_ids = fields.Many2many(
        comodel_name="account.move",
        relation="sale_advance_compensation_move_rel",
        column1="compensation_id",
        column2="move_id",
        string="Compensation Moves",
        copy=False,
        readonly=True,
    )

    @api.depends("amount", "applied_amount")
    def _compute_remaining_amount(self):
        for compensation in self:
            compensation.remaining_amount = max(
                compensation.amount - compensation.applied_amount, 0.0
            )

    @api.depends(
        "advance_line_id",
        "advance_line_id.amount_residual",
        "advance_invoice_id.payment_state",
    )
    def _compute_available_amount(self):
        for compensation in self:
            compensation._refresh_advance_line_from_invoice()
            compensation.available_amount = (
                compensation._get_available_amount()
                if compensation.advance_line_id
                else 0.0
            )

    @api.onchange("sale_order_id")
    def _onchange_sale_order_id(self):
        if self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id.commercial_partner_id
            self.company_id = self.sale_order_id.company_id
            self.currency_id = self.sale_order_id.currency_id

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._add_default_vals(vals.copy()) for vals in vals_list]
        records = super().create(vals_list)
        records._check_business_consistency()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._check_business_consistency()
        return res

    def _add_default_vals(self, vals):
        order = self.env["sale.order"].browse(vals.get("sale_order_id"))
        if order:
            vals.setdefault("partner_id", order.partner_id.commercial_partner_id.id)
            vals.setdefault("company_id", order.company_id.id)
            vals.setdefault("currency_id", order.currency_id.id)
        return vals

    @api.constrains("amount")
    def _check_amount(self):
        for compensation in self:
            if compensation.amount <= 0.0:
                raise ValidationError(
                    _("The compensation amount must be greater than zero.")
                )

    def _check_business_consistency(self):
        for compensation in self:
            order = compensation.sale_order_id
            advance_line = compensation.advance_line_id
            payment_term_line = compensation.payment_term_line_id
            if compensation.state == "cancelled":
                continue
            if not order or not payment_term_line:
                continue
            if compensation.company_id != order.company_id:
                raise ValidationError(
                    _("The compensation company must match the sale order company.")
                )
            if compensation.currency_id != order.currency_id:
                raise ValidationError(
                    _("The compensation currency must match the sale order currency.")
                )
            if payment_term_line.payment_id != order.payment_term_id:
                raise ValidationError(
                    _(
                        "The advance payment term line must belong to the sale "
                        "order payment term."
                    )
                )
            if not payment_term_line.is_advance:
                raise ValidationError(
                    _("The payment term line must be marked as an advance.")
                )
            if advance_line:
                if advance_line.account_id.account_type != "asset_prepayments":
                    raise ValidationError(
                        _("The selected line is not posted on a prepayment account.")
                    )
                if advance_line.company_id != order.company_id:
                    raise ValidationError(
                        _("The advance company must match the sale order company.")
                    )
                if not advance_line.account_id.reconcile:
                    raise ValidationError(
                        _("The advance account must allow reconciliation.")
                    )
                if advance_line.move_id.state != "posted":
                    raise ValidationError(
                        _("The advance journal entry must be posted.")
                    )
                if (
                    advance_line.partner_id.commercial_partner_id
                    != order.partner_id.commercial_partner_id
                ):
                    raise ValidationError(
                        _("The advance partner must match the sale order customer.")
                    )
            if (
                compensation.partner_id.commercial_partner_id
                != order.partner_id.commercial_partner_id
            ):
                raise ValidationError(
                    _("The compensation partner must match the sale order customer.")
                )

    def _get_available_amount(self):
        self.ensure_one()
        if not self.advance_line_id:
            return 0.0
        return max(abs(self.advance_line_id.amount_residual), 0.0)

    def _validate_reservation(self):
        self._check_business_consistency()
        for compensation in self:
            available = compensation._get_available_amount()
            amount_to_reserve = compensation.amount - compensation.applied_amount
            if compensation.advance_line_id and amount_to_reserve > available:
                raise ValidationError(
                    _(
                        "The amount %(amount)s exceeds the available advance "
                        "balance %(available)s."
                    )
                    % {"amount": amount_to_reserve, "available": available}
                )

    def action_reserve(self):
        to_reserve = self.filtered(lambda compensation: compensation.state == "draft")
        to_reserve._validate_reservation()
        to_reserve.state = "reserved"

    def action_create_advance_invoice(self):
        self.ensure_one()
        if self.advance_invoice_id:
            return self.advance_invoice_id
        if self.state == "cancelled":
            raise ValidationError(_("Cancelled advances cannot be invoiced."))
        if not self.sale_order_id.advance_product_id:
            raise ValidationError(_("Configure an Advance Product on the sale order."))
        wizard = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "fixed",
                "sale_order_ids": [(6, 0, self.sale_order_id.ids)],
                "fixed_amount": self.amount,
            }
        )
        invoice = wizard.with_context(
            sale_advance_product_id=self.sale_order_id.advance_product_id.id,
            skip_sale_advance_compensation=True,
        )._create_invoices(
            self.sale_order_id.with_context(skip_sale_advance_compensation=True)
        )
        invoice.skip_sale_advance_compensation = True
        invoice.invoice_payment_term_id = False
        if self.sale_order_id.advance_journal_id:
            invoice.journal_id = self.sale_order_id.advance_journal_id
        self.write(
            {
                "advance_invoice_id": invoice.id,
                "state": "invoiced",
            }
        )
        return invoice

    def action_open_advance_invoice(self):
        self.ensure_one()
        invoice = self.action_create_advance_invoice()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": invoice.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_cancel(self):
        self.filtered(
            lambda compensation: compensation.state in ("draft", "reserved", "invoiced")
        ).state = "cancelled"

    def _mark_invoiced(self, invoice):
        for compensation in self.filtered(
            lambda compensation: compensation.state == "reserved"
        ):
            vals = {
                "state": "invoiced",
                "invoice_ids": [(4, invoice.id)],
            }
            if not compensation.invoice_id:
                vals["invoice_id"] = invoice.id
            compensation.write(vals)

    def _register_application(self, invoice, move, amount):
        self.ensure_one()
        applied_amount = self.applied_amount + amount
        state = (
            "applied"
            if self.currency_id.compare_amounts(applied_amount, self.amount) >= 0
            else "invoiced"
        )
        self.write(
            {
                "invoice_id": invoice.id,
                "compensation_move_id": move.id,
                "invoice_ids": [(4, invoice.id)],
                "compensation_move_ids": [(4, move.id)],
                "applied_amount": applied_amount,
                "state": state,
            }
        )

    def _refresh_advance_line_from_invoice(self):
        for compensation in self.filtered(
            lambda record: record.advance_invoice_id and not record.advance_line_id
        ):
            line = compensation.advance_invoice_id.line_ids.filtered(
                lambda move_line: move_line.account_id.account_type
                == "asset_prepayments"
                and move_line.account_id.reconcile
                and move_line.amount_residual < 0.0
            )[:1]
            if line:
                compensation.advance_line_id = line
