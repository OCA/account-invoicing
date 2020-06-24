from odoo import models, api, fields


class InvoiceMergeAutoPayInvoice(models.Model):
    _inherit = 'account.invoice'

    auto_merge = fields.Boolean(
        # Override label and help only
        string=u'Pay automatically',
        help=u"Pay automatically at partner's next merge date",
    )

    @api.constrains('auto_merge', 'payment_mode_id')
    def _check_auto_merge(self):
        for inv in self:
            if inv.auto_merge and not inv.payment_mode_id:
                raise models.ValidationError(
                    'Payment mode is needed to auto pay an invoice')
