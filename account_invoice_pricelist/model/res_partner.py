# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_invoice_pricelist_id(self, invoice_type):
        self.ensure_one()
        pricelist_id = False
        if invoice_type in ['out_invoice', 'out_refund']:
            # Customer Invoices
            pricelist_id = self.property_product_pricelist.id
        elif invoice_type in ['in_invoice', 'in_refund']:
            # Supplier Invoices
            if self._model._columns.get(
                    'property_product_pricelist_purchase', False):
                pricelist_id =\
                    self.property_product_pricelist_purchase.id
        return pricelist_id
