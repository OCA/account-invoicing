from odoo import models, api, exceptions, _
from odoo.tools import float_compare, float_round


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_taxes_values(self):
        taxes_grouped = super().get_taxes_values()
        if self.company_id.tax_calculation_rounding_method == 'round_globally':
            tax_groups = self.invoice_line_ids.mapped('invoice_line_tax_ids')
            for key in taxes_grouped:
                for tax_group in tax_groups:
                    if taxes_grouped[key]['tax_id'] == tax_group.id:
                        taxes_recomputed = tax_group.compute_all(
                            taxes_grouped[key]['base'])
                        if any(t.get('price_include', False) for t
                               in taxes_recomputed['taxes']):
                            # no need to do this check for price included taxes
                            continue
                        amount_recomputed = sum(
                            [x['amount'] for x in taxes_recomputed['taxes']])
                        if float_compare(
                            amount_recomputed, taxes_grouped[key]['amount'],
                                precision_rounding=self.currency_id.rounding):
                            amount = float_round(
                                taxes_grouped[key]['amount'],
                                precision_rounding=self.currency_id.rounding
                            )
                            amount_recomputed = float_round(
                                amount_recomputed,
                                precision_rounding=self.currency_id.rounding
                            )
                            amount_diff = abs(float_round(
                                amount - amount_recomputed,
                                precision_rounding=self.currency_id.rounding
                            ))
                            tax_max_diff = self.env.user.company_id.\
                                tax_max_diff_global_rounding_method
                            if amount_diff > tax_max_diff:
                                raise exceptions.ValidationError(
                                    _('Global recompute of tax %s exceeds max '
                                      'tax diff allowed %s' % (
                                          tax_max_diff, amount_diff))
                                )
                            taxes_grouped[key]['amount'] = amount_recomputed
        return taxes_grouped
