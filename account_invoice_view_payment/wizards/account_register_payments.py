# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.multi
    def create_payment_and_open(self):
        payment = self.env['account.payment'].create(self.get_payment_vals())
        payment.post()
        res = {
            'res_id': payment.id,
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
