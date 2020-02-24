# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_timesheet_invoice_description = fields.Selection(
        selection="_get_timesheet_invoice_description",
        string="Timesheet Invoice Description",
        default_model="sale.order",
    )

    @api.model
    def _get_timesheet_invoice_description(self):
        return self.env["sale.order"]._get_timesheet_invoice_description()
