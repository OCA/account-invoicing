# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceSetDueDate(models.TransientModel):
    _name = 'account.invoice.set.due.date'
    _description = 'Wizard to set due date'

    date_due = fields.Date(
        string="New Due Date", required=True,
        help="New date to be set to the invoice's due date.")

    @api.multi
    def action_set_due_date(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.invoice':
            return False

        # Set due date on invoices
        invoices = self.env['account.invoice'].browse(active_ids)
        invoices.write({'date_due': self.date_due})

        # Set due date on account move lines
        amls = invoices.mapped('move_id.line_ids').filtered(
            lambda a: a.account_id == a.invoice_id.account_id)
        amls.write({'date_maturity': self.date_due})
        return True
