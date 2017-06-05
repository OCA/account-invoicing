# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    agent_invoice_id = fields.Many2one(
        'account.invoice', 'Agent Invoice', readonly=True)

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

            if 'fiscal_position' in agent_invoice_vals:
                # because it would typically be the same, with_fiscal_agent
                del agent_invoice_vals['fiscal_position']

            # Company ID
            agent_invoice_vals.update({
                'company_id': self.fiscal_position.fiscal_agent_company_id.id
            })

            # Mapping Journal
            agent_journal = \
                self.fiscal_position.map_agent_journal(self.journal_id)
            agent_invoice_vals.update({
                'journal_id': agent_journal.id
            })

            # Mapping Account
            agent_account = \
                self.fiscal_position.map_agent_account(self.account_id)
            agent_invoice_vals.update({
                'account_id': agent_account.id
            })

            # Looping over the invoice lines
            invoice_line_list = []
            for invoice_line in self.invoice_line:
                # Calling Product onchange Method
                invoice_line_vals = {
                    'product_id': invoice_line.product_id.id,
                    'name': invoice_line.name,
                    'quantity': invoice_line.quantity,
                    'price_unit': invoice_line.price_unit,
                    'uos_id': invoice_line.uos_id.id,
                }

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
            new_invoice_rec.invoice_validate()
            self.write({'agent_invoice_id': new_invoice_rec.id})
        return super(account_invoice, self).invoice_validate()

    @api.multi
    def action_cancel(self):
        super(account_invoice, self).action_cancel()
        invoice_model = self.env['account.invoice']
        for rec in self:
            if rec.agent_invoice_id:
                other_invoice = invoice_model.sudo().browse(
                    rec.agent_invoice_id.id)
                other_invoice.signal_workflow('invoice_cancel')
        return True
