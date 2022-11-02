# Copyright 2011-2020 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2014-2020 Akretion France (http://www.akretion.com)
# @author Mathieu Vatel <mathieu _at_ julius.fr>
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2022 FactorLibre - Luis J. Salvatierra <luis.salvatierra@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    fiscal_position_id = fields.Many2one(tracking=True)

    @api.onchange("fiscal_position_id")
    def _onchange_fiscal_position_id_account_invoice_fiscal_position_invoice(self):
        res = {}
        lines_without_product = self.env["account.move.line"]
        invoice_lines = self.invoice_line_ids.filtered(
            lambda l: "product" == l.display_type
        )
        for line in invoice_lines:
            if not line.product_id:
                lines_without_product |= line
            else:
                line._compute_tax_ids()
                line._compute_account_id()
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
                ) % ("\n- ".join(lines_without_product.mapped("name")))
        return res
