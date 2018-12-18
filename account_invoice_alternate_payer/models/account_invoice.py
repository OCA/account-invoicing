# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    alternate_payer_id = fields.Many2one(
        'res.partner', string='Alternate Payer',
        readonly=True, states={'draft': [('readonly', False)]},
        help="If set, this partner will be the that we expect to pay or to "
             "be paid by. If not set, the payor is by default the "
             "commercial")

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        if line.get('type', False) == 'dest' and self.alternate_payer_id:
            res['partner_id'] = self.alternate_payer_id.id
        return res

    @api.onchange('partner_id', 'company_id', 'alternate_payer_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        company_id = self.company_id.id
        domain = {}
        if self.type in ('in_invoice', 'out_refund') and \
                self.alternate_payer_id:
            bank_ids = self.alternate_payer_id.bank_ids.filtered(
                lambda b: b.company_id.id == company_id or not b.company_id)
            bank_id = bank_ids[0].id if bank_ids else False
            self.partner_bank_id = bank_id
            domain = {'partner_bank_id': [('id', 'in', bank_ids.ids)]}
        if domain:
            res['domain'] = domain
        if self.alternate_payer_id:
            account_id = False
            payment_term_id = False
            p = self.alternate_payer_id if not company_id else \
                self.alternate_payer_id.with_context(force_company=company_id)
            type = self.type
            if p:
                rec_account = p.property_account_receivable_id
                pay_account = p.property_account_payable_id
                if not rec_account and not pay_account:
                    action = self.env.ref('account.action_account_config')
                    msg = _(
                        'Cannot find a chart of accounts for this company, '
                        'You should configure it. \nPlease go to Account '
                        'Configuration.')
                    raise RedirectWarning(msg, action.id,
                                          _('Go to the configuration panel'))

                if type in ('out_invoice', 'out_refund'):
                    account_id = rec_account.id
                    payment_term_id = p.property_payment_term_id.id
                else:
                    account_id = pay_account.id
                    payment_term_id = p.property_supplier_payment_term_id.id
            self.account_id = account_id
            self.payment_term_id = payment_term_id
        return res
