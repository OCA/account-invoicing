# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
        compute="_compute_pricelist_id",
        inverse="_inverse_pricelist_id",
        tracking=True,
        store=True,
        precompute=True,
    )

    def _inverse_pricelist_id(self):
        for invoice in self:
            if (
                invoice.partner_id
                and invoice.is_sale_document()
                and invoice.partner_id.property_product_pricelist
                and not invoice.pricelist_id
            ):
                invoice.pricelist_id = invoice.partner_id.property_product_pricelist
