# -*- coding: UTF-8 -*-
# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _account_id_default(self):
        partner_id = self._context.get('partner_id')
        if not partner_id:
            return self._default_account()
        assert isinstance(partner_id, int), (
            _('No valid id for context partner_id %d') % partner_id)
        invoice_type = self._context.get('type')
        if invoice_type in ['in_invoice', 'in_refund']:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.property_account_expense:
                return partner.property_account_expense.id
        elif invoice_type in ['out_invoice', 'out_refund']:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.property_account_income:
                return partner.property_account_income.id
        return self._default_account()

    account_id = fields.Many2one(default=_account_id_default)

    @api.onchange('account_id')
    def _onchange_account_id(self):
        if not self.account_id or not self.partner_id or self.product_id:
            return super(AccountInvoiceLine, self)._onchange_account_id()
        if self._context.get('journal_id'):
            journal = self.env['account.journal'].browse(
                self._context.get('journal_id'))
            if self.account_id in [
                    journal.default_credit_account_id,
                    journal.default_debit_account_id]:
                return super(AccountInvoiceLine, self)._onchange_account_id()
        # We have a manually entered account_id (no product_id, so the
        # account_id is not the result of a product selection).
        # Store this account_id as future default in res_partner.
        inv_type = self._context.get('type', 'out_invoice')
        if (inv_type in ['in_invoice', 'in_refund'] and
                self.partner_id.auto_update_account_expense):
            if self.account_id != self.partner_id.property_account_expense:
                self.partner_id.write({
                    'property_account_expense': self.account_id.id})
        elif (inv_type in ['out_invoice', 'out_refund'] and
                self.partner_id.auto_update_account_income):
            if self.account_id != self.partner_id.property_account_income:
                self.partner_id.write({
                    'property_account_income': self.account_id.id})
        return super(AccountInvoiceLine, self)._onchange_account_id()
