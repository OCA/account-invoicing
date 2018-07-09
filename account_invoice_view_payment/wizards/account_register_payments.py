# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.multi
    def create_payment_and_open(self):
        payment_model = self.env['account.payment']
        payments = payment_model
        for payment_vals in self.get_payments_vals():
            payments += payment_model.create(payment_vals)
        payments.post()
        res = {
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'views': [(False, 'form')],
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
        return res
