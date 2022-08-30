# Copyright 2020 Akretion - Clément Mombereau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.osv import expression


class AccountMove(models.Model):
    _inherit = "account.move"

    def _link_timesheets_to_invoice_line(self, start_date=None, end_date=None):
        """Search timesheets from given period and link each timesheet to its related
        invoice line.

        Mimic '_link_timesheets_to_invoice' in native module 'sale_timesheet'
        """
        move_ids = self.filtered(
            lambda i: i.move_type == "out_invoice" and i.state == "draft"
        )

        for aml in move_ids.invoice_line_ids:
            sale_line_delivery = aml._get_sale_line_delivery()
            if sale_line_delivery:
                domain = [
                    ("so_line", "in", sale_line_delivery.ids),
                    ("project_id", "!=", False),
                    ("timesheet_invoice_id", "=", aml.move_id.id),
                ]
                if start_date:
                    domain = expression.AND([domain, [("date", ">=", start_date)]])
                if end_date:
                    domain = expression.AND([domain, [("date", "<=", end_date)]])

                timesheets = self.env["account.analytic.line"].sudo().search(domain)
                timesheets.write({"timesheet_invoice_line_id": aml.id})

    def _check_balanced(self):
        if self.env.context.get("split_aml_by_timesheets"):
            return

        return super()._check_balanced()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    timesheet_ids = fields.One2many(
        "account.analytic.line",
        "timesheet_invoice_line_id",
        string="Timesheets",
        readonly=True,
        copy=False,
    )

    # Filled by sale order line's _prepare_invoice_line()
    timesheet_invoice_description = fields.Char()
    timesheet_invoice_split = fields.Boolean("Split Order lines by timesheets")

    def _get_sale_line_delivery(self):
        return self.sale_line_ids.filtered(
            lambda sol: sol.product_id.invoice_policy == "delivery"
            and sol.product_id.service_type == "timesheet"
        )
