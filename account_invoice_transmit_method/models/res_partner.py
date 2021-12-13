# Copyright 2017-2020 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_invoice_transmit_method_id = fields.Many2one(
        "transmit.method",
        string="Customer Invoice Transmission Method",
        company_dependent=True,
        tracking=True,
        ondelete="restrict",
        domain=[("customer_ok", "=", True)],
    )
    customer_invoice_transmit_method_code = fields.Char(
        related="customer_invoice_transmit_method_id.code",
        string="Customer Invoice Transmission Method Code",
    )
    supplier_invoice_transmit_method_id = fields.Many2one(
        "transmit.method",
        string="Vendor Invoice Reception Method",
        company_dependent=True,
        tracking=True,
        ondelete="restrict",
        domain=[("supplier_ok", "=", True)],
    )
    supplier_invoice_transmit_method_code = fields.Char(
        related="supplier_invoice_transmit_method_id.code",
        string="Vendor Invoice Reception Method Code",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + [
            "customer_invoice_transmit_method_id",
            "supplier_invoice_transmit_method_id",
        ]
