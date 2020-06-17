from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    auto_merge = fields.Boolean(
        default=False,
        string='Merge automatically',
        help="Merge automatically at partner's next merge date",
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        result = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and self.type in ('out_invoice')\
                and self.partner_id.auto_merge_invoice:
            self.auto_merge = self.partner_id.auto_merge_invoice
        return result
