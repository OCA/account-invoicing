# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    reason_id = fields.Many2one('account.invoice.refund.reason',
                                string="Reason")

    @api.onchange('reason_id')
    def _onchange_reason_id(self):
        if self.reason_id:
            self.description = self.reason_id.name

    @api.multi
    def invoice_refund(self):
        res = super(AccountInvoiceRefund, self).invoice_refund()
        data_refund = self.read(['filter_refund'])[0]['filter_refund']
        if data_refund == 'modify':
            inv_id = res.get('res_id')
        else:
            inv_id = res.get('domain')[1][2][0]
        if inv_id:
            invoice = self.env['account.invoice'].browse(inv_id)
            invoice.reason_id = self.reason_id
        return res
