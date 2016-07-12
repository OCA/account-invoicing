# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestAccountInvoice(TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        self.inv_model = self.env['account.invoice']
        self.account_model = self.env['account.account']

    def test_action_move_create(self):
        invoice_account = self.account_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1).id

        # Creation of an invoice instance, wrong check_total
        with self.assertRaises(UserError):
            self.inv_model.create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'account_id': invoice_account,
                'type': 'in_invoice',
                'check_total': 1}).action_move_create()
