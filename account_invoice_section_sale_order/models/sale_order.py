# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import re
from collections import OrderedDict
from datetime import datetime

import pytz

from odoo import models
from odoo.tools.safe_eval import safe_eval, time


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Add sections by groups in the invoice line.

        Order the invoicing lines by groups and add lines section with
        the group name.
        Only do this for invoices targetting multiple groups
        """
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        for invoice in invoices.sudo():
            if invoice.line_ids and (
                len(invoice.line_ids.mapped(invoice.line_ids._get_section_grouping()))
                == 1
            ):
                continue
            sequence = 10
            # Because invoices are already created, this would require
            # an extra read access in order to read order fields.
            move_lines = invoice._get_ordered_invoice_lines()
            # Group move lines according to their sale order
            section_grouping_matrix = OrderedDict()
            for move_line in move_lines:
                group = move_line._get_section_group()
                section_grouping_matrix.setdefault(group, []).append(move_line.id)
            # Prepare section lines for each group
            section_lines = []
            for group, move_line_ids in section_grouping_matrix.items():
                if group:
                    section_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": group._get_invoice_section_name(),
                                "display_type": "line_section",
                                "sequence": sequence,
                                # see test: test_create_invoice_with_default_journal
                                # forcing the account_id is needed to avoid
                                # incorrect default value
                                "account_id": False,
                                # see test: test_create_invoice_with_currency
                                # if the currency is not set with the right value
                                # the total amount will be wrong
                                # because all line do not have the same currency
                                "currency_id": invoice.currency_id.id,
                            },
                        )
                    )
                    sequence += 10
                for move_line in (
                    self.env["account.move.line"].sudo().browse(move_line_ids)
                ):
                    # Because invoices are already created, this would require
                    # an extra write access in order to read order fields.
                    move_line.sequence = sequence
                    sequence += 10
            # Because invoices are already created, this would require
            # an extra write access in order to read order fields.
            invoice.line_ids = section_lines
        return invoices

    def localize(self, date_to_localize=None, strftime_var="%m-%d-%Y"):
        tz = self.env.user.tz
        if tz:
            local_tz = pytz.timezone(tz)
        else:
            local_tz = pytz.utc
        return (
            pytz.utc.localize(date_to_localize)
            .astimezone(local_tz)
            .strftime(strftime_var)
        )

    def _get_invoice_section_name(self):
        """Returns the text for the section name."""
        self.ensure_one()
        naming_scheme = (
            self.partner_invoice_id.invoice_section_name_scheme
            or self.company_id.invoice_section_name_scheme
        )

        if naming_scheme and "object" in naming_scheme:
            fields_to_localize = re.finditer(r"object.(\w+)", naming_scheme)
            for field_to_localize in fields_to_localize:
                object_field_name = field_to_localize.group(0).replace("object.", "")
                if not hasattr(self, object_field_name):
                    continue
                object_field = getattr(self, object_field_name)
                if isinstance(object_field, datetime):
                    strftime_pattern = re.compile(r".strftime\(.*?\)")
                    strftime_match = strftime_pattern.search(
                        naming_scheme, field_to_localize.end()
                    )
                    if strftime_match:
                        strftime_var = strftime_match.group(0)
                        naming_scheme = naming_scheme.replace(
                            f"{field_to_localize.group(0)}{strftime_var}",
                            self.localize(
                                object_field,
                                strftime_var.replace(".strftime(", "").replace(")", ""),
                            ),
                        )
        if naming_scheme:
            return safe_eval(naming_scheme, {"object": self, "time": time})
        elif self.client_order_ref:
            return "{} - {}".format(self.name, self.client_order_ref or "")
        else:
            return self.name
