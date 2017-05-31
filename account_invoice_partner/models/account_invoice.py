# -*- coding: utf-8 -*-
# Copyright 2013-2017 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """
        Replace the selected partner with the preferred invoice contact
        """
        partner_invoice_id = self.partner_id
        if self.partner_id:
            addr_ids = self.partner_id.address_get(adr_pref=['invoice'])
            partner_invoice_id = self.env['res.partner'].browse(
                addr_ids['invoice'])
        result = super(AccountInvoice, self)._onchange_partner_id()
        if partner_invoice_id != self.partner_id:
            self.partner_id = partner_invoice_id
        return result
