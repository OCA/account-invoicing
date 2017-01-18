# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    agent_invoice_id = fields.Many2one('account.invoice', 'Agent Invoice')

    @api.multi
    def invoice_validate(self):
        if self.fiscal_position and self.fiscal_position.with_fiscal_agent:
            # Getting basic data of invoice
            agent_invoice_vals = {
                'partner_id': self.partner_id.id,
                'date_invoice': self.date_invoice,
            }

            # Calling onchange method of partner_id
            partner_onchange_vals = self.onchange_partner_id(
                self.type,
                self.partner_id.id,
                self.date_invoice,
                self.payment_term,
                self.partner_bank_id and self.partner_bank_id.id or False,
                self.company_id and self.company_id.id or False)
            agent_invoice_vals.update(partner_onchange_vals.get('value'))

            # Company ID
            if self.company_id:
                agent_invoice_vals.update({
                    'company_id': self.company_id.id
                })

            # Mapping Journal
            agent_journal = False
            agent_journal = \
                self.fiscal_position.map_agent_journal(self.journal_id)
            agent_invoice_vals.update({
                'journal_id': agent_journal.id
            })

            # Mapping Account
            agent_account = False
            agent_account = \
                self.fiscal_position.map_agent_account(self.account_id)
            agent_invoice_vals.update({
                'account_id': agent_account.id
            })

            # Looping over the invoice lines
            invoice_line_list = []
            for invoice_line in self.invoice_line:
                # Calling Product onchange Method
                invoice_line_vals = {}
                product_onchange_vals = \
                    invoice_line.product_id_change(
                        invoice_line.product_id.id,
                        invoice_line.uos_id.id,
                        invoice_line.quantity,
                        invoice_line.name,
                        invoice_line.invoice_id.type,
                        invoice_line.partner_id.id,
                        invoice_line.invoice_id.fiscal_position and
                        invoice_line.invoice_id.fiscal_position.id or False,
                        invoice_line.price_unit,
                        invoice_line.invoice_id.currency_id and
                        invoice_line.invoice_id.currency_id.id or False,
                        invoice_line.company_id.id)
                invoice_line_vals.update(product_onchange_vals.get('value'))
                invoice_line_vals.update({
                    'product_id': invoice_line.product_id.id,
                    'quantity': invoice_line.quantity,
                })

                # Mapping line Taxes
                agent_taxes = self.fiscal_position.map_agent_taxes(
                    invoice_line.invoice_line_tax_id)
                if agent_taxes:
                    invoice_line_vals.update({
                        'invoice_line_tax_id': [(6, 0, agent_taxes.ids)],
                    })
                # Mapping Line Account
                agent_line_account = False
                agent_line_account = self.fiscal_position.map_agent_account(
                    invoice_line.account_id)
                invoice_line_vals.update({
                    'account_id': agent_line_account.id
                })
                invoice_line_list.append((0, 0, invoice_line_vals))

            # Adding the Invoice lines to the Invoice vals.
            if invoice_line_list:
                agent_invoice_vals.update({
                    'invoice_line': invoice_line_list
                })

            # Creating new Invoice
            new_invoice_rec = self.sudo().create(agent_invoice_vals)
            self.write({'agent_invoice_id': new_invoice_rec.id})
        return super(account_invoice, self).invoice_validate()

    @api.multi
    def action_cancel(self):
        super(account_invoice, self).action_cancel()
        for rec in self:
            if rec.agent_invoice_id:
                rec.agent_invoice_id.signal_workflow('invoice_cancel')
        return True
