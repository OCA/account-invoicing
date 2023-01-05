# Copyright 2022 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def copy_data(self, default=None):
        """Circumvent the inclusion of business fields depending on the context.

        This is used to allow the creation of credit notes without resetting the
        invoiced quantities on sales or purchases.
        """
        avoid_include_business_fields = self.env.context.get(
            "avoid_include_business_fields"
        ) and self.env.context.get("include_business_fields")
        if avoid_include_business_fields:
            self = self.with_context(include_business_fields=False)
        res = super().copy_data(default=default)
        if avoid_include_business_fields:
            # purchase_line_id is copied by default
            for _line, values in zip(self, res):
                if values.get("purchase_line_id"):
                    values.pop("purchase_line_id")
        return res
