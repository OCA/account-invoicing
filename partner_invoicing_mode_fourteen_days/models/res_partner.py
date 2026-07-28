# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.fields import Date


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoicing_mode = fields.Selection(
        selection_add=[("fourteen_days", "Each 14 days")],
        ondelete={"fourteen_days": "set default"},
    )

    def _update_next_invoice_date(self):
        """
        This will update the next invoice date from the configuration set on
        the partner if needed (not for standard invoicing_mode).
        """
        fourteen_days_partners = self.filtered(
            lambda partner: partner.invoicing_mode == "fourteen_days"
        )
        if fourteen_days_partners:
            today = Date.today()
            for partner in fourteen_days_partners:
                # We use the former date on partner to set the new one
                current_date = partner.next_invoice_date or today
                next_invoice_date = current_date + relativedelta(days=14)
                partner.write(
                    {
                        "next_invoice_date": next_invoice_date,
                    }
                )
        return super()._update_next_invoice_date()
