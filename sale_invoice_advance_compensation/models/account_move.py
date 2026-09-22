# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_advance_compensation_ids = fields.One2many(
        comodel_name="sale.advance.compensation",
        inverse_name="invoice_id",
        string="Sale Advance Compensations",
        readonly=True,
    )
    sale_advance_compensation_count = fields.Integer(
        compute="_compute_sale_advance_compensation_count",
    )
    skip_sale_advance_compensation = fields.Boolean(
        copy=False,
        readonly=True,
    )

    def _compute_sale_advance_compensation_count(self):
        compensation_model = self.env["sale.advance.compensation"]
        for move in self:
            move.sale_advance_compensation_count = compensation_model.search_count(
                [("invoice_ids", "in", move.ids)]
            )

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        posted.invalidate_recordset(["skip_sale_advance_compensation"])
        to_apply = posted.filtered(lambda move: not move.skip_sale_advance_compensation)
        if not self.env.context.get("skip_sale_advance_compensation"):
            to_apply._apply_reserved_sale_advance_compensations()
        return posted

    def _apply_reserved_sale_advance_compensations(self):
        for invoice in self.filtered(
            lambda move: move.state == "posted" and move.move_type == "out_invoice"
        ):
            invoice._apply_sale_advance_compensations()

    def _apply_sale_advance_compensations(self):
        self.ensure_one()
        compensations = self._get_sale_advance_compensations_to_apply()
        for compensation in compensations:
            compensation._refresh_advance_line_from_invoice()
            if not compensation.advance_line_id:
                continue
            invoice_line = self._get_advance_compensation_invoice_line()
            if not invoice_line:
                break
            amount = min(
                compensation.remaining_amount,
                abs(invoice_line.amount_residual),
                compensation._get_available_amount() + compensation.remaining_amount,
            )
            if self.currency_id.is_zero(amount):
                continue
            wizard = self.env["account.invoice.advance.compensation.wizard"].create(
                {
                    "move_id": self.id,
                    "invoice_line_id": invoice_line.id,
                    "advance_line_id": compensation.advance_line_id.id,
                    "journal_id": (
                        compensation.sale_order_id.advance_journal_id.id
                        or self.journal_id.id
                    ),
                    "amount": amount,
                    "date": self.invoice_date or fields.Date.context_today(self),
                }
            )
            wizard.with_context(
                skip_advance_journal_check=True
            )._validate_compensation()
            move = wizard._create_compensation_move()
            move.action_post()
            wizard._process_reconciliation(move)
            compensation._register_application(self, move, amount)

    def _get_sale_advance_compensations_to_apply(self):
        self.ensure_one()
        sale_orders = self.invoice_line_ids.sale_line_ids.order_id
        compensations = sale_orders.mapped("advance_compensation_ids").filtered(
            lambda compensation: compensation.state in ("reserved", "invoiced")
            and compensation.remaining_amount > 0.0
        )
        compensations._refresh_advance_line_from_invoice()
        compensations = compensations.filtered("advance_line_id")
        compensations._mark_invoiced(self)
        return compensations.sorted(lambda compensation: compensation.id)

    def _get_advance_compensation_invoice_line(self):
        self.ensure_one()
        return self.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
            and not line.reconciled
            and line.amount_residual
        )[:1]

    def action_view_sale_advance_compensations(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_invoice_advance_compensation.sale_advance_compensation_action"
        )
        action["domain"] = [("invoice_ids", "in", self.id)]
        action["context"] = {
            "default_invoice_id": self.id,
            "default_partner_id": self.partner_id.commercial_partner_id.id,
            "default_company_id": self.company_id.id,
            "default_currency_id": self.currency_id.id,
        }
        return action
