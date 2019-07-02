from odoo import models, fields


class InvoiceMergeAutoInvoice(models.Model):
    _inherit = 'account.invoice'

    auto_merge = fields.Boolean(
        default=False,
        string=u'Merge automatically',
        help=u"Merge automatically at partner's next merge date",
    )
