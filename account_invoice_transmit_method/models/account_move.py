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
        domain="['|', '&', ('customer_ok', '=', transmit_method_domain_sale),"
        "('customer_ok', '=', True),"
        "'&', ('supplier_ok', '=', transmit_method_domain_purchase),"
        " ('supplier_ok', '=', True)]",
    )
    # Field used to match specific invoice transmit method
    # to show/display fields/buttons, add constraints, etc...
    transmit_method_code = fields.Char(related="transmit_method_id.code", store=True)
    transmit_method_domain_sale = fields.Boolean(
        compute="_compute_transmit_method_domain", default=True
    )
    transmit_method_domain_purchase = fields.Boolean(
        compute="_compute_transmit_method_domain", default=True
    )

    @api.depends("type")
    def _compute_transmit_method_domain(self):
        """Compute fields specific to the domain applied on transmit_method_id.

        Because the field is displayed twice in the view the domain can not
        be set there (only the last one would be applied).
        Using api.onchange could be an option but does the domain is not
        applied when opening an exsiting record.

        """
        for record in self:
            if record.is_sale_document():
                record.transmit_method_domain_sale = True
                record.transmit_method_domain_purchase = False
            elif record.is_purchase_document():
                record.transmit_method_domain_sale = False
                record.transmit_method_domain_purchase = True
            else:
                record.transmit_method_domain_sale = True
                record.transmit_method_domain_purchase = True

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
        # TODO: Improvement make it computed and writeable instead, and drop
        #       This override
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
