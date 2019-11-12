# Author: Joël Grand-Guillaume (Camptocamp)
# Author: Dhara Solanki <dhara.solanki@initos.com>
# Copyright 2010-2015 Camptocamp SA
# Copyright initOS GmbH 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('to_send', 'To Send'),
            ('to_valid', 'To Validate'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Canceled')
        ], 'State', select=True, readonly=True)

    @api.multi
    def action_invoice_open(self):
        """ Allow to validate invoice in 'to_send' state."""
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: float_compare(
                inv.amount_total, 0.0,
                precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(
                _("You cannot validate an invoice with negative total amount."
                  "You should create a credit note instead."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

    @api.multi
    def action_to_valid(self):
        """Check if analytic account of each lines is not closed"""
        str_error_lines = ""
        errors = False
        for inv in self:
            for line in inv.invoice_line_ids:
                if line.account_analytic_id and \
                        line.account_analytic_id.state in ['close',
                                                           'cancelled']:
                    str_error_lines += "\n- %s" % line.name
                    errors = True
            if errors:
                raise UserError(
                    _("You are trying to validate invoice lines linked to a "
                      "closed or cancelled Analytic Account.\n\n"
                      "Check the following lines:") + str_error_lines)
        self.write({'state': 'to_valid'})

    @api.multi
    def action_to_send(self):
        self.write({'state': 'to_send'})
