# Copyright 2017-2021 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    transmit_method_id = fields.Many2one(
        "transmit.method",
        compute="_compute_transmit_method_id",
        readonly=False,
        store=True,
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
    transmit_method_code = fields.Char(
        related="transmit_method_id.code", store=True, string="Transmission Method Code"
    )
    transmit_method_domain_sale = fields.Boolean(
        compute="_compute_transmit_method_domain",
    )
    transmit_method_domain_purchase = fields.Boolean(
        compute="_compute_transmit_method_domain",
    )

    @api.depends("move_type")
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

    @api.depends("move_type", "partner_id", "company_id")
    def _compute_transmit_method_id(self):
        for move in self:
            tmethod_id = False
            if move.partner_id and move.move_type and move.company_id:
                partner = move.partner_id.with_company(move.company_id.id)
                if move.is_sale_document():
                    tmethod_id = partner.customer_invoice_transmit_method_id.id or False
                elif move.is_purchase_document():
                    tmethod_id = partner.supplier_invoice_transmit_method_id.id or False
            move.transmit_method_id = tmethod_id
