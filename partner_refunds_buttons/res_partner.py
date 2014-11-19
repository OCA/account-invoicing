# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Anthony Muschang
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from openerp import models, fields, api


class res_partner(models.Model):
    _inherit = "res.partner"

    supplier_refund_count = fields.Integer(
        compute='_invoice_count', string="# Supplier Refund",
        groups='account.group_account_invoice')

    customer_refund_count = fields.Integer(
        compute='_invoice_count', string="# Customer Refund",
        groups='account.group_account_invoice')

    customer_invoice_count = fields.Integer(
        compute='_invoice_count', string="# Invoice Count",
        groups='account.group_account_invoice')

    @api.one
    def _invoice_count(self):
        Invoice = self.env['account.invoice']

        self.supplier_refund_count = \
            Invoice.search_count([('partner_id', '=', self.id),
                                  ('type', '=', 'in_refund')])
        self.customer_refund_count = \
            Invoice.search_count([('partner_id', '=', self.id),
                                  ('type', '=', 'out_refund')])
        self.customer_invoice_count = \
            Invoice.search_count([('partner_id', '=', self.id),
                                  ('type', '=', 'out_invoice')])
