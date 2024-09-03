# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from collections import OrderedDict

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
        invoice_ids = super()._create_invoices(grouped=grouped, final=final, date=date)
        for invoice in invoice_ids:
            if (
                len(invoice.line_ids.mapped(invoice.line_ids._get_section_grouping()))
                == 1
            ):
                continue
            sequence = 10
            # Because invoices are already created, this would require
            # an extra read access in order to read order fields.
            move_lines = invoice.sudo()._get_ordered_invoice_lines()
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
                for move_line in self.env["account.move.line"].browse(move_line_ids):
                    # Because invoices are already created, this would require
                    # an extra write access in order to read order fields.
                    move_line.sudo().sequence = sequence
                    sequence += 10
            # Because invoices are already created, this would require
            # an extra write access in order to read order fields.
            invoice.sudo().line_ids = section_lines
        return invoice_ids

    def _get_invoice_section_name(self):
        """Returns the text for the section name."""
        self.ensure_one()
        naming_scheme = (
            self.partner_invoice_id.invoice_section_name_scheme
            or self.company_id.invoice_section_name_scheme
        )
        if naming_scheme:
            return safe_eval(naming_scheme, {"object": self, "time": time})
        elif self.client_order_ref:
            return "{} - {}".format(self.name, self.client_order_ref or "")
        else:
            return self.name
