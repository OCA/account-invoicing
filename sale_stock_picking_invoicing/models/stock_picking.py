# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_partner_to_invoice(self):
        partner_id = super()._get_partner_to_invoice()
        partner = self.env["res.partner"].browse(partner_id)
        if self.sale_id:
            if partner != self.sale_id.partner_invoice_id:
                partner_id = self.sale_id.partner_invoice_id.id

        return partner_id
