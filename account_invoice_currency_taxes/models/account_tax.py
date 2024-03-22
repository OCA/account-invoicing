# © 2023 FactorLibre - Javier Iniesta <javier.iniesta@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.tools.misc import formatLang


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
        res = super()._prepare_tax_totals(base_lines, currency, tax_lines)
        if not base_lines:
            return res

        record = base_lines[0]["record"]
        company_currency_id = record.env.company.currency_id
        if (
            record._name != "account.move.line"
            or not record.move_id.invoice_date
            or record.currency_id == company_currency_id
        ):
            return res

        res["display_company_currency_taxes"] = True
        invoice_id = record.move_id
        is_inbound = invoice_id.is_inbound()
        is_outbound = invoice_id.is_outbound()
        tax_line_ids = (invoice_id.line_ids - invoice_id.invoice_line_ids).filtered(
            lambda x: x.tax_line_id
        )

        group_tax_id_sum = {}
        for tax_line_id in tax_line_ids:
            group_tax_id_sum.setdefault(tax_line_id.tax_group_id.id, 0)
            if is_inbound:
                group_tax_id_sum[tax_line_id.tax_group_id.id] += (
                    tax_line_id.debit * -1 or tax_line_id.credit
                )
            elif is_outbound:
                group_tax_id_sum[tax_line_id.tax_group_id.id] += (
                    tax_line_id.debit or tax_line_id.credit * -1
                )

        for data_list in res["groups_by_subtotal"].values():
            for group in data_list:
                total_group_tax = 0
                if group["group_key"] in group_tax_id_sum.keys():
                    total_group_tax = group_tax_id_sum[group["group_key"]]
                group.update(
                    {
                        "formatted_tax_group_amount_company_currency": formatLang(
                            self.env, total_group_tax, currency_obj=company_currency_id
                        ),
                    }
                )

        return res
