# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    advance_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Advance Journal",
        check_company=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'sale')]",
        default=lambda self: self.env.company.sale_advance_journal_id,
        copy=False,
    )
    advance_compensation_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Advance Journal (Compatibility)",
        related="advance_journal_id",
        readonly=False,
    )
    advance_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Advance Product",
        check_company=True,
        domain="[('type', '=', 'service')]",
        default=lambda self: self.env.company.sale_advance_product_id,
        copy=False,
    )
    advance_compensation_ids = fields.One2many(
        comodel_name="sale.advance.compensation",
        inverse_name="sale_order_id",
        string="Advance Compensations",
        copy=False,
    )
    advance_compensation_count = fields.Integer(
        compute="_compute_advance_compensation_count",
    )
    advance_payment_term_line_ids = fields.Many2many(
        comodel_name="account.payment.term.line",
        compute="_compute_advance_payment_term_line_ids",
    )
    advance_compensation_amount = fields.Monetary(
        compute="_compute_advance_compensation_amounts",
        currency_field="currency_id",
    )
    advance_available_amount = fields.Monetary(
        compute="_compute_advance_compensation_amounts",
        currency_field="currency_id",
    )
    amount_after_compensation = fields.Monetary(
        compute="_compute_advance_compensation_amounts",
        currency_field="currency_id",
    )

    @api.depends(
        "amount_total",
        "advance_compensation_ids.amount",
        "advance_compensation_ids.applied_amount",
        "advance_compensation_ids.available_amount",
        "advance_compensation_ids.state",
        "partner_id",
        "company_id",
    )
    def _compute_advance_compensation_amounts(self):
        for order in self:
            active_compensations = order.advance_compensation_ids.filtered(
                lambda compensation: compensation.state != "cancelled"
            )
            order.advance_compensation_amount = sum(
                active_compensations.mapped("amount")
            )
            order.advance_available_amount = sum(
                active_compensations.mapped("available_amount")
            )
            order.amount_after_compensation = (
                order.amount_total - order.advance_compensation_amount
            )

    @api.depends("advance_compensation_ids")
    def _compute_advance_compensation_count(self):
        for order in self:
            order.advance_compensation_count = len(order.advance_compensation_ids)

    @api.depends("payment_term_id", "payment_term_id.line_ids.is_advance")
    def _compute_advance_payment_term_line_ids(self):
        for order in self:
            order.advance_payment_term_line_ids = (
                order.payment_term_id.line_ids.filtered("is_advance")
            )

    def action_confirm(self):
        self._sync_advance_compensations_from_payment_terms()
        for order in self.filtered("advance_payment_term_line_ids"):
            if not order.advance_product_id:
                raise UserError(
                    _(
                        "An Advance Product must be set on the sale order or in "
                        "Sales settings before confirming an order with advance "
                        "payment term lines."
                    )
                )
            order.advance_compensation_ids.action_reserve()
        return super().action_confirm()

    def action_cancel(self):
        res = super().action_cancel()
        self.mapped("advance_compensation_ids").action_cancel()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._sync_advance_compensations_from_payment_terms()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if {"payment_term_id", "order_line"} & set(vals):
            self._sync_advance_compensations_from_payment_terms()
        return res

    def _sync_advance_compensations_from_payment_terms(self):
        for order in self:
            order._sync_advance_compensations_from_payment_term()

    def _sync_advance_compensations_from_payment_term(self):
        self.ensure_one()
        active_compensations = self.advance_compensation_ids.filtered(
            lambda compensation: compensation.state != "cancelled"
        )
        advance_lines = self.payment_term_id.line_ids.filtered("is_advance")
        for compensation in active_compensations.filtered(
            lambda record: record.payment_term_line_id not in advance_lines
            and record.state in ("draft", "reserved")
        ):
            compensation.action_cancel()
        existing_by_term_line = {
            compensation.payment_term_line_id: compensation
            for compensation in active_compensations
            if compensation.payment_term_line_id in advance_lines
        }
        for term_line in advance_lines:
            amount = self._get_advance_amount_from_payment_term_line(term_line)
            if self.currency_id.is_zero(amount):
                continue
            compensation = existing_by_term_line.get(term_line)
            if compensation:
                if compensation.state in ("draft", "reserved"):
                    compensation.amount = amount
            else:
                self.env["sale.advance.compensation"].create(
                    {
                        "sale_order_id": self.id,
                        "payment_term_line_id": term_line.id,
                        "amount": amount,
                    }
                )

    def _get_advance_amount_from_payment_term_line(self, term_line):
        self.ensure_one()
        if term_line.value == "fixed":
            return term_line.value_amount
        return self.currency_id.round(
            self.amount_total * term_line.value_amount / 100.0
        )

    def _get_invoiceable_lines(self, final=False):
        lines = super()._get_invoiceable_lines(final=final)
        orders_with_compensation = self.filtered("advance_compensation_ids")
        if orders_with_compensation:
            lines = lines.filtered(
                lambda line: not (
                    line.order_id in orders_with_compensation and line.is_downpayment
                )
            )
        return lines

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        if self.env.context.get("skip_sale_advance_compensation"):
            invoices.skip_sale_advance_compensation = True
        for order in self:
            order._link_advance_compensations_to_invoices(invoices)
        return invoices

    def _link_advance_compensations_to_invoices(self, invoices):
        self.ensure_one()
        order_invoices = invoices.filtered(
            lambda move: self in move.invoice_line_ids.sale_line_ids.order_id
        )
        if not order_invoices:
            return
        compensations = self.advance_compensation_ids.filtered(
            lambda compensation: compensation.state == "reserved"
        )
        if compensations:
            compensations._mark_invoiced(order_invoices[0])

    def action_view_advance_compensations(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_invoice_advance_compensation.sale_advance_compensation_action"
        )
        action["domain"] = [("sale_order_id", "=", self.id)]
        action["context"] = {
            "default_sale_order_id": self.id,
            "default_partner_id": self.partner_id.commercial_partner_id.id,
            "default_company_id": self.company_id.id,
            "default_currency_id": self.currency_id.id,
        }
        return action

    def action_create_advance_invoices(self):
        for order in self:
            advances = order.advance_compensation_ids.filtered(
                lambda advance: not advance.advance_invoice_id
                and advance.state != "cancelled"
            )
            for advance in advances:
                advance.action_create_advance_invoice()
        if len(self) == 1:
            return self.action_view_invoice()
        return {"type": "ir.actions.act_window_close"}

    @api.model
    def _load_advance_compensation_demo_flow(self):
        order = self.env.ref(
            "sale_invoice_advance_compensation.sale_order_advance_demo",
            raise_if_not_found=False,
        )
        if not order or order.state not in ("draft", "sent"):
            return
        order.action_confirm()
        compensation = order.advance_compensation_ids[:1]
        if not compensation:
            return
        advance_invoice = compensation.action_create_advance_invoice()
        advance_invoice.action_post()
        bank_journal = self.env.ref(
            "sale_invoice_advance_compensation.journal_advance_bank_demo"
        )
        payment_wizard = (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_ids=advance_invoice.ids,
                active_id=advance_invoice.id,
            )
            .create(
                {
                    "payment_date": fields.Date.context_today(self),
                    "journal_id": bank_journal.id,
                }
            )
        )
        payment_wizard._create_payments()
        final_invoice = order._create_invoices(final=True)
        (final_invoice - advance_invoice).action_post()
