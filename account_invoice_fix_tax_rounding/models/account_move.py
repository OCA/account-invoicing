from odoo import _, exceptions, models
from odoo.tools import float_round


class AccountMove(models.Model):
    _inherit = "account.move"

    def _preprocess_taxes_map(self, taxes_map):
        taxes_map = super()._preprocess_taxes_map(taxes_map)
        if self.company_id.tax_calculation_rounding_method == "round_globally":
            prec = self.currency_id.decimal_places + 2
            for taxes_map_entry in taxes_map.values():
                amount_recomputed = float_round(taxes_map_entry["amount"], prec)
                tax_max_diff = self.company_id.tax_max_diff_global_rounding_method
                amount_diff = abs(amount_recomputed - taxes_map_entry["amount"])
                if amount_diff > tax_max_diff:
                    raise exceptions.ValidationError(
                        _("Global recompute of tax %s exceeds max tax diff allowed %s")
                        % (amount_diff, tax_max_diff)
                    )
                taxes_map_entry["amount"] = amount_recomputed
        return taxes_map
