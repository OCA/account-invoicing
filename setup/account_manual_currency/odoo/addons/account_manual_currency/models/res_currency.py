import inspect

from odoo import api, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_rates(self, company, date, currency_table=None):
        """Compat 16 ↔ 17/18 : ignora currency_table si la firma base no lo admite."""
        custom_rate = self.env.context.get("custom_rate")
        to_currency = self.env.context.get("to_currency")

        # ----------- llamada a super con o sin kwarg ---------------
        base_get_rates = super()._get_rates
        if "currency_table" in inspect.signature(base_get_rates).parameters:
            rates = base_get_rates(company, date, currency_table=currency_table)
        else:  # camino Odoo 16
            rates = base_get_rates(company, date)
        # -----------------------------------------------------------

        # aplicar tasa manual si procede
        if custom_rate and to_currency:
            for cid in self.ids:
                rates[to_currency.id][cid] = custom_rate
        return rates
