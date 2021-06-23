# Copyright 2011-2020 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2014-2020 Akretion France (http://www.akretion.com)
# @author Mathieu Vatel <mathieu _at_ julius.fr>
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        fiscal_position = self.fiscal_position_id
        res = super()._onchange_partner_id()
        if fiscal_position != self.fiscal_position_id:
            self._onchange_fiscal_position_id_account_invoice_fiscal_position_invoice()
        return res

    @api.onchange("fiscal_position_id")
    def _onchange_fiscal_position_id_account_invoice_fiscal_position_invoice(self):
        """Updates taxes and accounts on all invoice lines"""
        res = {}
        lines_without_product = []
        invoice_lines = self.invoice_line_ids.filtered(lambda l: not l.display_type)
        for line in invoice_lines:
            if line.product_id:
                line.account_id = line._get_computed_account()
                taxes = line._get_computed_taxes()
                if taxes and line.move_id.fiscal_position_id:
                    taxes = line.move_id.fiscal_position_id.map_tax(
                        taxes, partner=line.partner_id
                    )
                line.tax_ids = taxes
                line._onchange_price_subtotal()
                line._onchange_mark_recompute_taxes()
            else:
                lines_without_product.append(line.name)
        self._onchange_invoice_line_ids()
        if lines_without_product:
            res["warning"] = {"title": _("Warning")}
            if len(lines_without_product) == len(invoice_lines):
                res["warning"]["message"] = _(
                    "The invoice lines were not updated to the new "
                    "Fiscal Position because they don't have products. "
                    "You should update the Account and the Taxes of each "
                    "invoice line manually."
                )
            else:
                res["warning"]["message"] = _(
                    "The following invoice lines were not updated "
                    "to the new Fiscal Position because they don't have a "
                    "Product:\n - %s\nYou should update the Account and the "
                    "Taxes of these invoice lines manually."
                ) % ("\n- ".join(lines_without_product))
        return res
