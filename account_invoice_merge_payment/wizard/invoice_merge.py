
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class InvoiceMerge(models.TransientModel):
    _inherit = "invoice.merge"

    @api.model
    def _dirty_check(self):
        res = super()._dirty_check()
        if self.env.context.get('active_model', '') == 'account.invoice':
            ids = self.env.context['active_ids']
            invs = self.env['account.invoice'].browse(ids)
            inv_diff = invs.filtered(
                lambda inv: inv.payment_mode_id != invs[0].payment_mode_id)
            if inv_diff:
                raise UserError(
                    _('Not all invoices use the same payment mode !'))
        return res
