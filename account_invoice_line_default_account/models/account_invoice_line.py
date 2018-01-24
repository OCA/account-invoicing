# -*- coding: UTF-8 -*-
# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)

from openerp.osv import orm
from openerp.tools.translate import _


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    def _account_id_default(self, cr, uid, context=None):
        if context is None:
            context = {}
        partner_id = context.get('partner_id')
        if not partner_id:
            return False
        assert isinstance(partner_id, (int, long)), (
            _('No valid id for context partner_id %d') % partner_id)
        invoice_type = context.get('type')
        partner_model = self.pool.get('res.partner')
        if invoice_type in ['in_invoice', 'in_refund']:
            partner = partner_model.read(
                cr, uid, partner_id,
                ['property_account_expense'], context=context)
            if partner['property_account_expense']:
                return partner['property_account_expense']
        elif invoice_type in ['out_invoice', 'out_refund']:
            partner = partner_model.read(
                cr, uid, partner_id,
                ['property_account_income'], context=context)
            if partner['property_account_income']:
                return partner['property_account_income']
        return self._default_account(cr, uid, context=context)

    _defaults = {
        'account_id': _account_id_default,
    }

    def onchange_account_id(
            self, cr, uid, ids, product_id, partner_id, inv_type,
            fposition_id, account_id, context=None):
        if not account_id or not partner_id or product_id:
            return super(account_invoice_line, self).onchange_account_id(
                cr, uid, ids, product_id, partner_id, inv_type,
                fposition_id, account_id)
        context = context or {}
        if context.get('journal_id'):
            journal = self.pool['account.journal'].browse(
                cr, uid, context.get('journal_id'), context=context)
            if account_id in [
                    journal.default_credit_account_id.id,
                    journal.default_debit_account_id.id]:
                return super(account_invoice_line, self).onchange_account_id(
                    cr, uid, ids, product_id, partner_id, inv_type,
                    fposition_id, account_id)
        # We have a manually entered account_id (no product_id, so the
        # account_id is not the result of a product selection).
        # Store this account_id as future default in res_partner.
        partner_model = self.pool.get('res.partner')
        partner = partner_model.read(
            cr, uid, partner_id,
            ['auto_update_account_expense', 'property_account_expense',
             'auto_update_account_income', 'property_account_income'],
            context=context)
        vals = {}
        if (inv_type in ['in_invoice', 'in_refund'] and
                partner['auto_update_account_expense']):
            if account_id != partner['property_account_expense']:
                # only write when something really changed
                vals.update({'property_account_expense': account_id})
        elif (inv_type in ['out_invoice', 'out_refund'] and
                partner['auto_update_account_income']):
            if account_id != partner['property_account_income']:
                # only write when something really changed
                vals.update({'property_account_income': account_id})
        if vals:
            partner_model.write(cr, uid, partner_id, vals, context=context)
        return super(account_invoice_line, self).onchange_account_id(
            cr, uid, ids, product_id, partner_id, inv_type,
            fposition_id, account_id)
