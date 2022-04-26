# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)
# Copyright 2022 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        partner = self.invoice_id.partner_id
        invoice_type = self.invoice_id.type
        if partner and invoice_type:
            if invoice_type in ['in_invoice', 'in_refund']:
                if partner.property_account_expense:
                    self.account_id = partner.property_account_expense.id
            elif invoice_type in ['out_invoice', 'out_refund']:
                if partner.property_account_income:
                    self.account_id = partner.property_account_income.id
        return res

    @api.onchange('account_id')
    def _onchange_default_partner_account(self):
        # Return early if partner's account does not have to be updated
        if not self.account_id or not self.partner_id or self.product_id:
            # There is no account, no partner to save the accounts into,
            # or there is a product that might have set the accounts
            return
        if self.env.context.get('journal_id'):
            journal = self.env['account.journal'].browse(
                self.env.context.get('journal_id'))
            if self.account_id in [
                    journal.default_credit_account_id,
                    journal.default_debit_account_id]:
                # The account has been set by the journal
                return

        # We have a manually entered account_id (no product_id, so the
        # account_id is not the result of a product selection).
        # Store this account_id as future default in res_partner.
        # `write`ing in an onchange is bad,
        # but `update`ing the partner does not work.
        inv_type = self.env.context.get('type', 'out_invoice')
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
