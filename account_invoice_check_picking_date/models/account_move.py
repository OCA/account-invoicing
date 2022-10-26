# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.tools import config


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_min_max_stock_move_dates(self):
        self.ensure_one()
        moves = self._stock_account_get_last_step_stock_moves()
        min_date = moves[:1].date
        max_date = min_date
        for move in moves:
            if move.date < min_date:
                min_date = move.date
            if move.date > max_date:
                max_date = move.date
        return min_date, max_date

    def _match_invoice_and_stock_move_dates(self, min_date, max_date):
        self.ensure_one()
        if not max_date:
            return True
        return self.invoice_date.month == max_date.month

    def action_post(self):
        if config["test_enable"] or self.env.context.get(
            "skip_account_invoice_check_picking_date", False
        ):
            return super().action_post()
        invoice_types = (
            (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "account_invoice_check_picking_date.invoice_types", "in_invoice"
                )
            )
            .replace(" ", "")
            .split(",")
        )
        for invoice in self:
            if invoice.invoice_date and invoice.move_type in invoice_types:
                min_date, max_date = invoice._get_min_max_stock_move_dates()
                if invoice._match_invoice_and_stock_move_dates(min_date, max_date):
                    continue
                DateField = self.env["ir.qweb.field.date"]
                exception_msg = _(
                    "Invoice date: %s\n"
                    "First stock move: %s   Last stock move: %s\n\n"
                    "If dates are right and you have manager permissions you can use "
                    "special action to post this invoice."
                ) % (
                    DateField.value_to_html(invoice.invoice_date, {}),
                    DateField.value_to_html(min_date, {}),
                    DateField.value_to_html(max_date, {}),
                )
                exception_wizard = self.env["invoice.picking.date.check.wiz"].create(
                    {"exception_msg": exception_msg, "invoice_id": invoice.id}
                )
                return exception_wizard.action_show()
        return super().action_post()
