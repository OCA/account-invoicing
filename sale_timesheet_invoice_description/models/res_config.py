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
    default_timesheet_invoice_split = fields.Selection(
        selection="_get_timesheet_invoice_split",
        string="Split Order lines by",
        default_model="sale.order",
        default=SaleOrder.timesheet_invoice_split.default,
        required=SaleOrder.timesheet_invoice_split.required,
    )
    default_timesheet_invoice_consecutive = fields.Selection(
        selection="_get_timesheet_invoice_consecutive",
        string="Timesheets for consecutive Invoices",
        default_model="sale.order",
        default=SaleOrder.timesheet_invoice_consecutive.default,
        required=SaleOrder.timesheet_invoice_consecutive.required,
    )

    @api.model
    def _get_timesheet_invoice_description(self):
        return self.env["sale.order"]._get_timesheet_invoice_description()

    @api.model
    def _get_timesheet_invoice_split(self):
        return self.env["sale.order"]._get_timesheet_invoice_split()

    @api.model
    def _get_timesheet_invoice_consecutive(self):
        return self.env["sale.order"]._get_timesheet_invoice_consecutive()
