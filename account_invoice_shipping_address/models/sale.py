# -*- coding: utf-8 -*-

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def _prepare_invoice(self,):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
            'address_shipping_id': self.partner_shipping_id.id, })
        return res
