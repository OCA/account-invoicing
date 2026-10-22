# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoicing_mode = fields.Selection(
        selection_add=[("ten_days", "Each ten days")],
        ondelete={"ten_days": "set default"},
    )

    def _update_next_invoice_date(self):
        """
        This will update the next invoice date from the configuration set on
        the partner if needed (not for standard invoicing_mode).
        """
        today = fields.Datetime.now()
        ten_days_partners = self.filtered(
            lambda partner: partner.invoicing_mode == "ten_days"
        )
        if ten_days_partners:
            rows = [10, 20, (today + relativedelta(day=31)).day]
            try:
                next_day = next(row for row in rows if today.day < row)
                next_invoice_date = today.replace(day=next_day)
            except StopIteration:
                next_day = rows[0]
                next_invoice_date = (today + relativedelta(months=+1)).replace(
                    day=next_day
                )
            ten_days_partners.write(
                {
                    "next_invoice_date": next_invoice_date,
                }
            )
        return super()._update_next_invoice_date()
