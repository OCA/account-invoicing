# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = "account.move"

    def _get_ordered_invoice_lines(self):
        """Sort invoice lines according to the section ordering"""
        return self.invoice_line_ids.sorted(
            key=self.env["account.move.line"]._get_section_ordering()
        )


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _get_section_group(self):
        """Return the section group to be used for a single invoice line"""
        self.ensure_one()
        return self.mapped(self._get_section_grouping())

    def _get_section_grouping(self):
        """Defines the grouping relation from the invoice lines to be used.

        Meant to be overriden, in order to allow custom grouping.
        """
        invoice_section_grouping = self.company_id.invoice_section_grouping
        if invoice_section_grouping == "sale_order":
            return "sale_line_ids.order_id"
        raise UserError(_("Unrecognized invoice_section_grouping"))

    @api.model
    def _get_section_ordering(self):
        """Function to sort invoice lines before grouping"""
        return lambda r: r.mapped(r._get_section_grouping())
