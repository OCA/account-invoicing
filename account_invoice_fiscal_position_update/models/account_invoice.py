# Copyright 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2014 Akretion (http://www.akretion.com)
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
            self.fiscal_position_change()
        return res

    @api.onchange("fiscal_position_id")
    def fiscal_position_change(self):
        """Updates taxes and accounts on all invoice lines"""
        self.ensure_one()
        res = {}
        lines_without_product = []
        fp = self.fiscal_position_id
        inv_type = self.type
        for line in self.invoice_line_ids:
            if line.product_id:
                account = line._get_computed_account()
                product = line.with_context(force_company=self.company_id.id).product_id
                if inv_type in ("out_invoice", "out_refund"):
                    # M2M fields don't have an option 'company_dependent=True'
                    # so we need per-company post-filtering
                    taxes = product.taxes_id.filtered(
                        lambda tax: tax.company_id == self.company_id
                    )
                else:
                    taxes = product.supplier_taxes_id.filtered(
                        lambda tax: tax.company_id == self.company_id
                    )
                taxes = taxes or account.tax_ids.filtered(
                    lambda tax: tax.company_id == self.company_id
                )
                if fp:
                    taxes = fp.map_tax(taxes)

                line.tax_ids = [(6, 0, taxes.ids)]

                line.account_id = account.id
            else:
                lines_without_product.append(line.name)

        if lines_without_product:
            res["warning"] = {"title": _("Warning")}
            if len(lines_without_product) == len(self.invoice_line_ids):
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
                    "Product: - %s You should update the Account and the "
                    "Taxes of these invoice lines manually."
                ) % ("- ".join(lines_without_product))
        return res
