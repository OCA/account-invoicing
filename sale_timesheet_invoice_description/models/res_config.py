# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .sale import SaleOrder


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_timesheet_invoice_description = fields.Selection(
        selection="_get_timesheet_invoice_description",
        string="Timesheet Invoice Description",
        default_model="sale.order",
        default=SaleOrder.timesheet_invoice_description.default,
        required=SaleOrder.timesheet_invoice_description.required,
    )

    @api.model
    def _get_timesheet_invoice_description(self):
        return self.env["sale.order"]._get_timesheet_invoice_description()
