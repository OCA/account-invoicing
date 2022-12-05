# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = "sale.order"

    timesheet_invoice_description = fields.Selection(
        "_get_timesheet_invoice_description", default="000"
    )
    timesheet_invoice_split = fields.Boolean("Split Order lines by timesheets")

    @api.model
    def _get_timesheet_invoice_description(self):
        return [
            ("000", _("None")),
            ("111", _("Date - Time spent - Description")),
            ("101", _("Date - Description")),
            ("001", _("Description")),
            ("011", _("Time spent - Description")),
        ]

    def _get_timesheet_details(self, timesheet, desc_rule):
        details = []
        if desc_rule[0] == "1":
            details.append(fields.Date.to_string(timesheet.date))
        if desc_rule[1] == "1":
            details.append(
                "{} {}".format(timesheet.unit_amount, timesheet.product_uom_id.name)
            )
        if desc_rule[2] == "1":
            details.append(timesheet.name)
        return details

    def _get_timesheet_description_list(self, timesheet_ids, desc_rule):
        """Returns a list of timesheets description"""
        desc_list = []
        for timesheet_id in timesheet_ids.sorted(lambda t: t.date):
            details = self._get_timesheet_details(timesheet_id, desc_rule)
            desc_list.append(" - ".join(map(lambda x: str(x) or "", details)))
        return desc_list

    def _split_aml_by_timesheets(self, aml, ts_ids, desc_list):
        """Split an invoice line in as many lines as there is related timesheets,
        taking care to convert timesheets quantities in the invoice line's UoM"""
        aml_total = aml.quantity
        aml_uom_id = aml.product_uom_id
        aml_seq = aml.sequence
        aml_sum = 0
        ts_ids = ts_ids.sorted(lambda t: t.date)

        # Add a line section on top before the original aml
        self.env["account.move.line"].create(
            {
                "name": aml.name,
                "sequence": aml_seq - 1,
                "display_type": "line_section",
                "move_id": aml.move_id.id,
            }
        )

        # Override the original aml values with first timesheet
        init_ts_uom_id = ts_ids[0].product_uom_id
        init_ts_qty = ts_ids[0].unit_amount
        init_qty = init_ts_uom_id._compute_quantity(init_ts_qty, aml_uom_id)
        aml_sum += init_qty

        aml.with_context(split_aml_by_timesheets=True).write(
            {
                "name": desc_list[0],
                "quantity": init_qty,
            }
        )

        # Create one invoice line for each timesheet except the last one
        for index, ts_id in enumerate(ts_ids[1:-1]):
            ts_uom_id = ts_id.product_uom_id
            ts_qty = ts_id.unit_amount
            qty = ts_uom_id._compute_quantity(ts_qty, aml_uom_id)
            new_aml = aml.with_context(split_aml_by_timesheets=True).copy()
            new_aml.with_context(split_aml_by_timesheets=True).write(
                {
                    "name": desc_list[index + 1],
                    "sequence": aml_seq + index + 1,
                    "quantity": qty,
                    "sale_line_ids": aml.sale_line_ids.ids,
                }
            )
            aml_sum += qty
        # Last new invoice line get the rest
        if ts_ids[-1] != ts_ids[0]:
            last_qty = aml_total - aml_sum
            last_aml = aml.with_context(split_aml_by_timesheets=True).copy()
            last_aml.write(
                {
                    "name": desc_list[-1],
                    "sequence": aml_seq + len(ts_ids) - 1,
                    "quantity": last_qty,
                    "sale_line_ids": aml.sale_line_ids.ids,
                }
            )

    def _create_invoices(
        self, grouped=False, final=False, start_date=None, end_date=None
    ):
        """Override the native _create_invoice method in order to :
        1. link the new invoices lines with their related timesheets
        2. change their names consequently
        """
        # Additional condition to avoid beaking third party tests expecting to create
        # invoices lines the standard way
        is_third_party_test = config["test_enable"] and not self.env.context.get(
            "test_timesheet_description"
        )

        moves = super()._create_invoices(grouped=grouped, final=final)
        moves._link_timesheets_to_invoice_line(start_date=start_date, end_date=end_date)

        for move_id in moves:
            for aml in move_id.invoice_line_ids:
                ts_ids = aml.timesheet_ids
                desc_rule = aml.timesheet_invoice_description
                inv_split = aml.timesheet_invoice_split
                desc_list = self._get_timesheet_description_list(ts_ids, desc_rule)
                if (
                    desc_list
                    and desc_rule
                    and desc_rule != "000"
                    and not is_third_party_test
                ):
                    if inv_split:
                        self._split_aml_by_timesheets(aml, ts_ids, desc_list)
                    else:
                        desc = "\n".join(map(lambda x: str(x) or "", desc_list))
                        new_name = aml.name + "\n" + desc
                        aml.write({"name": new_name})

        return moves


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        desc_rule = self.order_id.timesheet_invoice_description
        inv_split = self.order_id.timesheet_invoice_split
        res.update(
            {
                "timesheet_invoice_description": desc_rule,
                "timesheet_invoice_split": inv_split,
            }
        )
        return res
