# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    reason_id = fields.Many2one('account.invoice.refund.reason',
                                string="Reason to credit")

    @api.onchange('reason_id')
    def _onchange_reason_id(self):
        if self.reason_id:
            self.description = self.reason_id.name

    @api.multi
    def compute_refund(self, mode='refund'):
        res = super().compute_refund(mode)
        context = dict(self._context or {})
        inv_obj = self.env['account.invoice']
        for inv in inv_obj.browse(self.env.context.get('active_ids')):
            inv.reason_id = self.reason_id.id
        return res
