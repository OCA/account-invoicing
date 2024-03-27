# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_fields_to_copy_recurring_entries(self, values):
        """Include customer ref in recurring entries."""
        values = super()._get_fields_to_copy_recurring_entries(values)
        if self.ref:
            values["ref"] = self.ref
        return values
