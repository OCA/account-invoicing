# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.account.models.account_invoice import TYPE2JOURNAL
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_corrispettivi_sale(self):
        self.corrispettivi = self.partner_id.use_corrispettivi

    corrispettivi = fields.Boolean()

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        journal_model = self.env['account.journal']
        if self.corrispettivi:
            invoice_vals['journal_id'] = journal_model \
                .get_corr_journal(self.company_id).id
        elif invoice_vals['journal_id']:
            # Be sure that the selected journal is not corrispettivi
            journal = journal_model.browse(invoice_vals['journal_id'])
            if journal.corrispettivi:
                # Default journal chosen by invoice is a corrispettivi,
                # then do the same as account_invoice to look for another
                # one that is not corrispettivi
                invoice_vals['journal_id'] = \
                    self._default_journal_not_corr().id
        return invoice_vals

    def _default_journal_not_corr(self):
        # Copied from account_invoice default behavior
        if self._context.get('default_journal_id', False):
            journal = self.env['account.journal'] \
                          .browse(self._context.get('default_journal_id'))
            if not journal.corrispettivi:
                return journal
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context \
            .get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', [_f
                            for _f in map(TYPE2JOURNAL.get, inv_types) if _f]),
            ('company_id', '=', company_id),
            ('corrispettivi', '=', False)  # with this tiny modification
        ]
        return self.env['account.journal'].search(domain, limit=1)
