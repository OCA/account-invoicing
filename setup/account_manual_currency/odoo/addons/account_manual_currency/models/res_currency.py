from odoo import api, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_rates(self, company, date, currency_table=None):
        """
        Odoo 17/18 añade el arg ``currency_table``.
        Para mantener compatibilidad en 16.0, quitamos el kwargs extra
        si la versión base no lo acepta.
        """
        custom_rate = self.env.context.get("custom_rate")
        to_currency = self.env.context.get("to_currency")

        # Llamada a super(), descartando currency_table si no existe
        if "currency_table" in self._get_rates.__code__.co_varnames:
            rates = super()._get_rates(
                company, date, currency_table=currency_table
            )
        else:  # pragma: no cover  (camino 16.0)
            rates = super()._get_rates(company, date)

        # aplicar tipo de cambio manual
        if custom_rate and to_currency:
            for cid in self.ids:
                rates[to_currency.id][cid] = custom_rate
        return rates
