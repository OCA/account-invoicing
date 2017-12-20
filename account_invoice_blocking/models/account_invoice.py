# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def _get_move_line(self):
        """
        This method searches for payable or receivable move line
        of the invoice
        :returns payable or receivable move line of the invoice
        """
        self.ensure_one()
        type_receivable = self.env.ref('account.data_account_type_receivable')
        type_payable = self.env.ref('account.data_account_type_payable')
        return self.env['account.move.line'].search(
            [('account_id.user_type_id', 'in', [type_receivable.id,
                                                type_payable.id]),
             ('invoice_id', '=', self.id)])

    @api.multi
    def _update_blocked(self, value):
        """
        This method updates the boolean field 'blocked' of the move line
        of the passed invoice with the passed value. If the invoice is in
        draft (=no journal entry), we update the 'draft_blocked' invoice field
        :param value: value to set to the 'blocked' field of the move line
        """
        self.ensure_one()
        if self.move_id:
            move_line_ids = self._get_move_line()
            move_line_ids.write({'blocked': value})
        else:
            self.write({'draft_blocked': value})

    @api.multi
    def _set_move_blocked(self):
        """
        Inverse method of the computed field 'blocked'
        This method calls the update of the invoice's move line based on
        the value of the field 'blocked'
        """
        for invoice in self:
            invoice._update_blocked(invoice.blocked)

    @api.multi
    def action_move_create(self):
        """
        This method overrides the invoice's move line creation
        This method calls the update of the invoice's move lines based on
        the value of the field 'draft_blocked'
        """
        res = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            invoice._update_blocked(invoice.draft_blocked)
        return res

    @api.depends(
        'draft_blocked',
        'move_id.line_ids.blocked',
        'move_id.line_ids.account_id.user_type_id',
    )
    def _get_move_blocked(self):
        """
        This method set the value of the field 'invoice.blocked' to True
        If every line of the invoice's move is actualy blocked or if the
        invoice is in draft and has been blocked.
        """
        for invoice in self:
            if not invoice.move_id:
                invoice.blocked = invoice.draft_blocked
                continue

            move_lines = invoice._get_move_line()
            invoice.blocked = move_lines and\
                all(line.blocked for line in move_lines) or False

    blocked = fields.Boolean(
        string='No Follow-up',
        compute='_get_move_blocked',
        inverse='_set_move_blocked',
        store=True,
    )

    draft_blocked = fields.Boolean(
        string='No Follow-up',
        help="This flag facilitates the blocking of the invoice's move lines.",
        copy=False,
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(AccountInvoice, self).fields_get(
            allfields=allfields, attributes=attributes)
        # Remove the draft blocked field from the custom search view
        if 'draft_blocked' in res:
            res['draft_blocked']['searchable'] = False
        return res
