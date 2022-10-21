# Copyright 2022 Aures TIC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoicing_mode_multi_monthday_last_execution = fields.Datetime(
        string="Last execution",
        help="Last execution of multi monthday invoicing.",
        readonly=True,
    )
    invoicing_mode_multi_monthday_days = fields.Char(
        string="Month days to invoice",
        help="Month days to invoice (sepparated with commas)",
    )

    def write(self, values):
        if "invoicing_mode_multi_monthday_days" in values:
            values[
                "invoicing_mode_multi_monthday_days"
            ] = self.fix_typo_comma_sepparated(
                values.get("invoicing_mode_multi_monthday_days")
            )
        return super(ResCompany, self).write(values)

    @api.model
    def fix_typo_comma_sepparated(self, days):
        return ",".join(
            filter(
                lambda val: val and val.isnumeric() and 0 < int(val) < 31,
                days.split(","),
            )
        )

    def get_invoicing_month_days(self):
        self.ensure_one()
        return (
            self.invoicing_mode_multi_monthday_days
            and map(int, self.invoicing_mode_multi_monthday_days.split(","))
            or []
        )
