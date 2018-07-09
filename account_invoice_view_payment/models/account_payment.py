# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post_and_open_payment(self):
        self.post()
        res = {
            'domain': "[('id','in', ["+','.join(map(str, self.ids))+"])]",
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
        if len(self.ids) == 1:
            res['views'] = [(False, 'form')]
            res['res_id'] = self.id
        return res
