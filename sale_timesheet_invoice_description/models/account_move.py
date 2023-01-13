# Copyright 2020 Akretion - Clément Mombereau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

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

        invoiced = defaultdict(float)  # timesheet ID to already invoiced qty

        for aml in move_ids.invoice_line_ids:
            sale_line_delivery = aml._get_sale_line_delivery()
            if sale_line_delivery:
                domain = [
                    ("so_line", "in", sale_line_delivery.ids),
                    ("project_id", "!=", False),
                    # Note: No longer consider only timesheets assigned to this
                    # invoice, as that will miss the ones that are only
                    # partially invoiced yet, e.g. through a manual change of
                    # their invoice line's quantity. Instead, we will filter
                    # for the desired timesheets below.
                    # ("timesheet_invoice_id", "=", aml.move_id.id),
                ]
                if start_date:
                    domain = expression.AND([domain, [("date", ">=", start_date)]])
                if end_date:
                    domain = expression.AND([domain, [("date", "<=", end_date)]])

                timesheets = self.env["account.analytic.line"].sudo().search(domain)

                # determine already invoiced quantities per timesheet
                # Caveats:
                # * Works only if the timesheet is actually invoiced on just a
                #   single invoice line (or none at all), since timesheets can
                #   only be associated with a single invoice line through field
                #   `timesheet_invoice_line_id`. There is no way to determine
                #   all invoice lines a timesheet is invoiced on.
                # * Works only if the association of an invoice line to the
                #   timesheet has not been undone, e.g., by deleting an invoice
                #   the timesheet had been invoiced on.
                for ts in timesheets:
                    inv_line = ts.timesheet_invoice_line_id
                    if inv_line:
                        # possibly multiple timesheets invoiced on same line
                        sheets = inv_line.timesheet_ids
                        qty_sum = sum(line.unit_amount for line in sheets)
                        # convert invoice line quantity to timesheet UoM
                        qty = inv_line.quantity
                        uom = inv_line.product_uom_id
                        qty = uom._compute_quantity(qty, ts.product_uom_id)
                        # Since there is no other way to known what fraction of
                        # this timesheet had been invoiced, do assume that the
                        # invoiced quantity for this timesheet is proportional
                        # to the total invoiced quantity of the line.
                        # This is correct if the invoice line does invoice only
                        # this single timesheet, but unclear if multiple.
                        invoiced[ts.id] = ts.unit_amount * qty / qty_sum

                # Filter out fully and/or partially invoiced timesheets,
                # depending on the according configuration option.
                def _to_be_invoiced(timesheet):
                    if aml.timesheet_invoice_consecutive == "uninvoiced":
                        return timesheet.id not in invoiced
                    # else: i.e., "not_fully_invoiced"
                    return invoiced[timesheet.id] < timesheet.unit_amount

                timesheets = timesheets.filtered(_to_be_invoiced)
                timesheets.write({"timesheet_invoice_line_id": aml.id})

        return invoiced

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
    # Technical hint: We keep `Selection` fields as `Char`. This is
    # intentionally done, in order to avoid code duplication (e.g., the need to
    # specify their `selection` parameter). Note that they are not available to
    # the Odoo users, but rather used just "internally" in the code. And there,
    # on code as well as database level, the values of `Selection` and `Char`
    # fields are just the same, namely strings. Hence, this works just fine.
    timesheet_invoice_description = fields.Char(
        readonly=True,
    )
    timesheet_invoice_split = fields.Char(
        string="Split Order lines by",
        readonly=True,
    )
    timesheet_invoice_consecutive = fields.Char(
        string="Timesheets for consecutive Invoices",
        readonly=True,
    )

    def _get_sale_line_delivery(self):
        return self.sale_line_ids.filtered(
            lambda sol: sol.product_id.invoice_policy == "delivery"
            and sol.product_id.service_type == "timesheet"
        )
