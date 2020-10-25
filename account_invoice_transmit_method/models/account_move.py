# Copyright 2017-2020 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    transmit_method_id = fields.Many2one(
        "transmit.method",
        string="Transmission Method",
        tracking=True,
        ondelete="restrict",
    )  # domain is set by @api.onchange("type")
    # Field used to match specific invoice transmit method
    # to show/display fields/buttons, add constraints, etc...
    transmit_method_code = fields.Char(related="transmit_method_id.code", store=True)

    @api.onchange("type")
    def _transmit_method_type_change(self):
        res = {"domain": {}}
        if self.is_sale_document():
            res["domain"]["transmit_method_id"] = "[('customer_ok', '=', True)]"
        elif self.is_purchase_document():
            res["domain"]["transmit_method_id"] = "[('supplier_ok', '=', True)]"
        return res

    @api.onchange("partner_id", "company_id")
    def _transmit_method_partner_change(self):
        if self.partner_id and self.type:
            if self.type in ("out_invoice", "out_refund"):
                self.transmit_method_id = (
                    self.partner_id.customer_invoice_transmit_method_id.id or False
                )
            else:
                self.transmit_method_id = (
                    self.partner_id.supplier_invoice_transmit_method_id.id or False
                )
        else:
            self.transmit_method_id = False

    @api.model
    def create(self, vals):
        if (
            "transmit_method_id" not in vals
            and vals.get("type")
            and vals.get("partner_id")
        ):
            partner = self.env["res.partner"].browse(vals["partner_id"])
            if vals["type"] in ("out_invoice", "out_refund"):
                vals["transmit_method_id"] = (
                    partner.customer_invoice_transmit_method_id.id or False
                )
            else:
                vals["transmit_method_id"] = (
                    partner.supplier_invoice_transmit_method_id.id or False
                )
        return super().create(vals)
