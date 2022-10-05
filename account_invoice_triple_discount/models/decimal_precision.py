# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class DecimalPrecision(models.Model):
    _inherit = "decimal.precision"

    def precision_get(self, application):
        return self.env.context.get(
            "with_precision", super(DecimalPrecision, self).precision_get(application)
        )
