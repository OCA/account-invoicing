# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account - Pricelist on Invoices for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Column Section
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist', string='Pricelist',
        compute='compute_pricelist_id', store=True,
        help="The pricelist of the partner, when the invoice is created"
                " or the partner has changed. This is a technical field used"
                " to reporting.")

    # Compute Section
    @api.one
    @api.depends('partner_id')
    def compute_pricelist_id(self):
        partner_obj = self.env['res.partner']
        if 'active_test' in self._context.keys():
            # Module is installing we have to manage multi company case
            # which current user is not on the company of the invoices
            partner = partner_obj.with_context(
                force_company=self.company_id.id).browse(self.partner_id.id)
        else:
            partner = self.partner_id

        if self.type in ('out_invoice', 'out_refund'):
            # Customer Invoices
            self.pricelist_id =\
                partner.property_product_pricelist.id
        elif self.type in ('in_invoice', 'in_refund'):
            # Supplier Invoices
            if self.partner_id._model._columns.get(
                    'property_product_pricelist_purchase', False):
                self.pricelist_id =\
                    partner.property_product_pricelist_purchase.id
