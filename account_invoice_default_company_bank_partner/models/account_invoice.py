# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp import models, api, _
from openerp.exceptions import RedirectWarning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        account_id = False
        payment_term_id = False
        fiscal_position = False
        bank_id = False
        default_company_bank_id = False

        if partner_id:
            p = self.env['res.partner'].browse(partner_id)
            rec_account = p.property_account_receivable
            pay_account = p.property_account_payable
            if company_id:
                if rec_account.company_id and \
                    rec_account.company_id.id != company_id\
                        and pay_account.company_id \
                        and pay_account.company_id.id != company_id:
                    prop = self.env['ir.property']
                    rec_dom = [('name', '=', 'property_account_receivable'),
                               ('company_id', '=', company_id)]
                    pay_dom = [('name', '=', 'property_account_payable'),
                               ('company_id', '=', company_id)]
                    res_dom = [('res_id', '=', 'res.partner,%s' % partner_id)]
                    rec_prop = prop.search(
                        rec_dom + res_dom) or prop.search(rec_dom)
                    pay_prop = prop.search(
                        pay_dom + res_dom) or prop.search(pay_dom)
                    rec_account = rec_prop.get_by_record(rec_prop)
                    pay_account = pay_prop.get_by_record(pay_prop)
                    if not rec_account and not pay_account:
                        action = self.env.ref('account.action_account_config')
                        msg = _(
                            'Cannot find a chart of accounts for this company, \
                            You should configure it. '
                            '\nPlease go to Account Configuration.')
                        raise RedirectWarning(msg, action.id, _(
                            'Go to the configuration panel'))

            if type in ('out_invoice', 'out_refund'):
                account_id = rec_account.id
                payment_term_id = p.property_payment_term.id
            else:
                account_id = pay_account.id
                payment_term_id = p.property_supplier_payment_term.id
            fiscal_position = p.property_account_position.id
            bank_id = p.bank_ids and p.bank_ids[0].id or False

            if p.default_company_bank_id:
                default_company_bank_id = p.default_company_bank_id

        result = {'value': {
            'account_id': account_id,
            'payment_term': payment_term_id,
            'fiscal_position': fiscal_position,
            'partner_bank_id': default_company_bank_id,
        }}

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != payment_term_id:
            if payment_term_id:
                to_update = self.onchange_payment_term_date_invoice(
                    payment_term_id, date_invoice)
                result['value'].update(to_update.get('value', {}))
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(bank_id)
            result['value'].update(to_update.get('value', {}))

        return result
