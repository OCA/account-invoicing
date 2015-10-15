# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _get_orders_procurements(self):
        res = super(SaleOrder, self)._get_orders_procurements()
        res['incoterm'] = self.incoterm.id
        return res
