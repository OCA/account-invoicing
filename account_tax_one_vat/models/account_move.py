# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_invoice_line_only_one_vat_tax(self):
        errors = []
        error_template = _("Invoice has a line %s with more than one vat tax")
        loggedin_company = self.env.company
        for invoice_line in self.invoice_line_ids.filtered(
            lambda x: x.display_type not in ("line_section", "line_note")
        ):
            company = invoice_line.company_id or loggedin_company
            vat_taxes = invoice_line._get_vat_taxes("tax_ids", company)
            if len(vat_taxes) > 1:
                error_string = error_template % invoice_line.name
                errors.append(error_string)
        if errors:
            raise UserError(
                _(
                    "%(message)s\n%(errors)s",
                    message="Multiple VAT Taxes Defined!",
                    errors=("\n".join(x for x in errors)),
                )
            )

    def action_post(self):
        for move in self:
            if move.move_type != "entry":
                move._check_invoice_line_only_one_vat_tax()
        return super().action_post()
