# -*- coding: utf-8 -*-
# Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
# Copyright (C) 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# Copyright 2017 Apulia Software srl - www.apuliasoftware.it
# Author Andrea Cometa <a.cometa@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_invoice(self, order, lines):

        res = super(SaleOrder, self)._prepare_invoice(order, lines)
        res['address_shipping_id'] = order.partner_shipping_id.id
        return res
