# -*- coding: utf-8 -*-
# © 2011 Domsense s.r.l. (<http://www.domsense.com>).
# © 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# © 2016 Farid Shahy (<fshahy@gmail.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self, context=None):

        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'address_shipping_id': self.partner_shipping_id.id, })
        return invoice_vals
