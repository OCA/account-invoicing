# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.tools import config, format_date


class SaleOrder(models.Model):
    _inherit = "sale.order"

    timesheet_invoice_description = fields.Selection(
        "_get_timesheet_invoice_description",
        default="000",
        required=True,
    )
    timesheet_invoice_split = fields.Selection(
        "_get_timesheet_invoice_split",
        string="Split Order lines by",
        help="How to split the order lines - by timesheet, by task, or not at all.",
    )
    timesheet_invoice_consecutive = fields.Selection(
        "_get_timesheet_invoice_consecutive",
        string="Timesheets for consecutive Invoices",
        default="not_fully_invoiced",
        required=True,
        help="Which timesheets are to be invoiced on consecutive invoices - "
        "only the yet completely uninvoiced (i.e., to ignore the already "
        "partially or fully invoiced), or also the already partially invoiced "
        "(i.e., to ignore only the already fully invoiced).",
    )

    @api.model
    def _get_timesheet_invoice_description(self):
        return [
            ("000", _("None")),
            ("111", _("Date - Time spent - Description")),
            ("101", _("Date - Description")),
            ("001", _("Description")),
            ("011", _("Time spent - Description")),
        ]

    @api.model
    def _get_timesheet_invoice_split(self):
        return [
            ("timesheet", _("Timesheet")),
            ("task", _("Task")),
        ]

    @api.model
    def _get_timesheet_invoice_consecutive(self):
        return [
            ("uninvoiced", _("Only uninvoiced")),
            ("not_fully_invoiced", _("Uninvoiced and partially invoiced")),
        ]

    def _get_timesheet_details(self, account_move_line, timesheet):
        desc_rule = account_move_line.timesheet_invoice_description
        details = []
        if not desc_rule:
            return details
        if desc_rule[0] == "1":
            lang = account_move_line.move_id.partner_id.lang
            date = format_date(self.env, timesheet.date, lang_code=lang)
            details.append(date)
        if desc_rule[1] == "1":
            details.append(
                "{} {}".format(timesheet.unit_amount, timesheet.product_uom_id.name)
            )
        if desc_rule[2] == "1":
            details.append(timesheet.name)
        return details

    def _get_timesheet_descriptions(self, account_move_line):
        """Returns a dict of an invoice line's timesheets' descriptions"""
        desc_dict = {}
        for timesheet_id in account_move_line.timesheet_ids:
            details = self._get_timesheet_details(account_move_line, timesheet_id)
            desc_dict[timesheet_id] = " - ".join(details)
        return desc_dict

    def _split_aml_accumulate_qty_of_group(self, group, aml_uom_id, invoiced):
        """The total quantity for a group of timesheets"""
        result = 0
        for ts_id in group:
            ts_uom_id = ts_id.product_uom_id
            ts_qty = ts_id.unit_amount - invoiced[ts_id.id]
            result += ts_uom_id._compute_quantity(ts_qty, aml_uom_id)
        return result

    def _split_aml_compile_group_description(self, group, desc_dict, inv_split):
        """The invoice line's label"""
        group_desc = []
        if inv_split == "task":
            task = group[0].task_id if group else None
            if task:
                group_desc += [task.name]
        group_desc += [desc_dict[ts_id] for ts_id in group if ts_id in desc_dict]
        return "\n".join(group_desc).strip()

    def _split_aml_by_timesheets(
        self, inv_split, aml, ts_ids, desc_dict, aml_seq, invoiced
    ):
        """
        Split an invoice line in as many lines as there are related timesheets
        or tasks (depending on the type of split);
        taking care to convert timesheets quantities in the invoice line's UoM
        """
        aml_uom_id = aml.product_uom_id
        aml_sum = 0
        ts_ids = ts_ids.sorted(lambda t: (t.date, t.task_id.id or 0))

        # the total amount not yet invoiced for this line
        aml_total = aml.quantity
        # the total remaining amount of the desired associated timesheets
        group_total = self._split_aml_accumulate_qty_of_group(
            ts_ids, aml_uom_id, invoiced
        )
        # In principle, this is the amount we want to invoice now. However, due
        # to rounding effects when involving different UoM's between timesheets
        # and their invoice line, this value may be larger than the uninvoiced
        # total `aml_total`.
        # Hence, we have to consider the minimum of the two.
        # Example: Let the invoice line consist of three timesheets with
        # 10.50 h (Hours) each, but let the invoice line's UoM be d (Days).
        # Then the total of the timesheets is 31.5 h, which is rounded to the
        # invoice line's `aml_total` of 3.94 d. But the individual timesheets
        # have an amount of 1.32 d each, accumulating to 3.96 d, which is
        # larger than the invoice line's `aml_total`.
        aml_total = min(group_total, aml_total)

        # Don't check the invoice balance while still doing the splitting.
        # An "intermediate" invoice may be unbalanced, and this would raise an
        # (unwanted) exception.
        # This is done by using `with_context(split_aml_by_timesheets=True)`.
        # Then, at the end, the taxes are recomputed, so that the invoice is
        # balanced again. See below.

        # group the timesheets
        # .... either by task, or individually
        if inv_split == "task":
            groups = defaultdict(ts_ids.browse)
            for ts in ts_ids:
                groups[ts.task_id] |= ts
            groups = list(groups.values())
        else:  # i.e., inv_split == "timesheet"
            groups = list(ts_ids)

        # Add a line section on top before the original aml
        self.env["account.move.line"].create(
            {
                "name": aml.name,
                "sequence": aml_seq,
                "display_type": "line_section",
                "move_id": aml.move_id.id,
            }
        )
        aml_seq += 1

        # Override the original aml values with first timesheet/task
        group = groups[0]
        if group != groups[-1]:
            # first one is not the last one, hence compute normally
            init_qty = self._split_aml_accumulate_qty_of_group(
                group, aml_uom_id, invoiced
            )
        else:
            # first one is the last one, hence assign the rest (see also below)
            init_qty = aml_total - aml_sum  # note that here, aml_sum == 0
        desc = self._split_aml_compile_group_description(group, desc_dict, inv_split)
        aml_sum += init_qty
        aml.with_context(split_aml_by_timesheets=True).write(
            {
                "name": desc or aml.name,
                "sequence": aml_seq,
                "quantity": init_qty,
            }
        )
        aml_seq += 1
        # note: updating invoice line on timesheets should not be necessary
        group.write({"timesheet_invoice_line_id": aml.id})

        # Create one invoice line for each timesheet/task except the last one
        for group in groups[1:-1]:
            qty = self._split_aml_accumulate_qty_of_group(group, aml_uom_id, invoiced)
            desc = self._split_aml_compile_group_description(
                group, desc_dict, inv_split
            )
            new_aml = aml.with_context(split_aml_by_timesheets=True).copy()
            new_aml.with_context(split_aml_by_timesheets=True).write(
                {
                    "name": desc or new_aml.name,
                    "sequence": aml_seq,
                    "quantity": qty,
                    "sale_line_ids": aml.sale_line_ids.ids,
                }
            )
            aml_seq += 1
            aml_sum += qty
            # update invoice line on timesheets
            group.write({"timesheet_invoice_line_id": new_aml.id})

        # Last new invoice line get the rest
        group = groups[-1]
        if group != groups[0]:
            last_qty = aml_total - aml_sum
            desc = self._split_aml_compile_group_description(
                group, desc_dict, inv_split
            )
            last_aml = aml.with_context(split_aml_by_timesheets=True).copy()
            last_aml.write(
                {
                    "name": desc or last_aml.name,
                    "sequence": aml_seq,
                    "quantity": last_qty,
                    "sale_line_ids": aml.sale_line_ids.ids,
                }
            )
            aml_seq += 1
            # update invoice line on timesheets
            group.write({"timesheet_invoice_line_id": last_aml.id})

        # Finally, recompute the (sub)total and taxes so that they all are
        # still correct.
        # Note that splitting could result in tax values on the split lines
        # that differ from the total tax of their original "unsplit" line,
        # thus resulting in incorrect invoice totals.
        # For example, say the original line has total = 400 with included
        # tax = 63.87, and it is split into two lines of total = 200 each.
        # These then will have tax = 31.93 each, for a tax sum = 63.86.
        # Which is 0.01 less than the original's tax.
        # In the end this means that the invoice's (sub)total and tax lines
        # have to be recomputed.
        move = aml.move_id.with_context(split_aml_by_timesheets=True)
        move._recompute_dynamic_lines(
            recompute_all_taxes=True, recompute_tax_base_amount=True
        )

        return aml_seq

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

        # The wizard "sale.advance.payment.inv" method `create_invoices()` does
        # provide the start and end date in the context rather than the kwargs.
        # Note that they are read from there in the super method in module
        # "sale_timesheet". Which is overwritten here without a super call.
        # Also note that the unit tests do use the kwarg.
        # Therefore, this method does accept the kwargs (for use with the unit
        # tests), but falls back to the context in case values for the kwargs
        # are not provided (as by the wizard).
        start_date = start_date or self.env.context.get("timesheet_start_date")
        end_date = end_date or self.env.context.get("timesheet_end_date")

        moves = super()._create_invoices(grouped=grouped, final=final)
        invoiced = moves._link_timesheets_to_invoice_line(
            start_date=start_date, end_date=end_date
        )

        for move_id in moves:
            aml_seq = 0
            for aml in move_id.invoice_line_ids:
                ts_ids = aml.timesheet_ids

                # Note that the method `_link_timesheets_to_invoice_line` of
                # account.move.line already filtered out the desired timesheets
                # (account.analytic.line), as there the timesheets' many2one
                # field 'timesheet_invoice_line_id' is set accordingly, and
                # this is the counterpart of the account.move.line's one2many
                # field 'timesheet_ids'.

                desc_rule = aml.timesheet_invoice_description
                inv_split = aml.timesheet_invoice_split
                desc_dict = self._get_timesheet_descriptions(aml)
                if (
                    desc_dict
                    and desc_rule
                    and (desc_rule != "000" or inv_split == "task")
                    and not is_third_party_test
                ):
                    if inv_split:
                        aml_seq = self._split_aml_by_timesheets(
                            inv_split, aml, ts_ids, desc_dict, aml_seq, invoiced
                        )
                    else:
                        desc_list = desc_dict.values()
                        desc = "\n".join(desc_list)
                        if desc:
                            new_name = aml.name + "\n" + desc
                            aml.write({"name": new_name.strip()})
                        # keep sequence of invoice lines
                        aml.write({"sequence": aml_seq})
                        aml_seq += 1
                else:
                    # keep sequence of invoice lines
                    aml.write({"sequence": aml_seq})
                    aml_seq += 1

        return moves


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        desc_rule = self.order_id.timesheet_invoice_description
        inv_split = self.order_id.timesheet_invoice_split
        inv_consecutive = self.order_id.timesheet_invoice_consecutive
        res.update(
            {
                "timesheet_invoice_description": desc_rule,
                "timesheet_invoice_split": inv_split,
                "timesheet_invoice_consecutive": inv_consecutive,
            }
        )
        return res
