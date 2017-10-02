# -*- coding: utf-8 -*-
# Copyright 2010 - 2014 Savoir-faire Linux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    customer_ref_strip = fields.Char(
        compute='_compute_customer_ref_strip', store=True)

    @api.multi
    @api.depends('name')
    def _compute_customer_ref_strip(self):
        for invoice in self:
            if invoice.type not in ['out_invoice', 'out_refund']:
                return True
            if invoice.name:
                invoice.customer_ref_strip = invoice.name.lower()
    _sql_constraints = [
        ('unique_customer_ref_strip', 'UNIQUE('
         'customer_ref_strip, company_id, commercial_partner_id)',
         _('The customer reference must be unique for '
           'each customer !'))]
