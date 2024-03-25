# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)
# Copyright 2022 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.fields import first


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        super()._compute_account_id()
        lines_without_product = self.filtered(
            lambda line: line.display_type == "product" and not line.product_id
        )
        if not lines_without_product:
            return
        # Lines could be updated at once grouped by invoice
        for _move, lines in lines_without_product.partition("move_id").items():
            partner = lines.move_id.partner_id
            invoice_type = lines.move_id.move_type
            if (
                invoice_type in ["in_invoice", "in_refund"]
                and partner.property_account_expense
            ):
                lines.account_id = partner.property_account_expense
            elif (
                invoice_type in ["out_invoice", "out_refund"]
                and partner.property_account_income
            ):
                lines.account_id = partner.property_account_income

    def write(self, vals):
        res = super().write(vals)
        self._update_partner_income_expense_default_accounts()
        return res

    def _get_updateable_income_expense_lines(self):
        """
        Return lines:
            - With an account
            - With a partner
            - Without a product
            - Without the account set from the journal
        """
        return self.filtered(
            lambda line: (
                line.display_type == "product"
                and line.account_id
                and line.move_id.partner_id
                and not line.product_id
            )
            and not (
                line.journal_id
                and line.account_id == line.journal_id.default_account_id
            )
        )

    def _update_partner_income_expense_default_accounts(self):
        """
        Update the partner default account.
        As the account is unique on partner and to avoid too
        much writes, group lines per invoice and update with the first line
        account
        """
        for invoice, lines in self.partition("move_id").items():
            line_to_update = first(lines._get_updateable_income_expense_lines())
            if not line_to_update:
                continue
            inv_type = invoice.move_type
            if (
                inv_type in ["in_invoice", "in_refund"]
                and invoice.partner_id.auto_update_account_expense
            ):
                if (
                    line_to_update.account_id
                    != invoice.partner_id.property_account_expense
                ):
                    invoice.partner_id.write(
                        {"property_account_expense": line_to_update.account_id.id}
                    )
            elif (
                inv_type in ["out_invoice", "out_refund"]
                and invoice.partner_id.auto_update_account_income
            ):
                if (
                    line_to_update.account_id
                    != invoice.partner_id.property_account_income
                ):
                    invoice.partner_id.write(
                        {"property_account_income": line_to_update.account_id.id}
                    )
