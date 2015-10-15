# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_partner_id(self):
        return (
            self.picking_id and self.picking_id.partner_id
            and self.picking_id.partner_id.id)

    @api.model
    def _get_product_id(self):
        return self.product_id and self.product_id.id

    @api.model
    def _get_categ_id(self):
        return (
            self.product_id and self.product_id.categ_id
            and self.product_id.categ_id.id)
