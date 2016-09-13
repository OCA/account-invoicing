# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError
from ..models.account_invoice import GROUP_AICT


class TestAccountInvoice(TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        # ENVIRONEMENTS

        self.account_invoice = self.env['account.invoice']
        self.account_model = self.env['account.account']
        self.account_invoice_line = self.env['account.invoice.line']
        self.current_user = self.env.user
        # Add current user to group: group_supplier_inv_check_total
        self.env.ref(GROUP_AICT).write({'users': [(4, self.current_user.id)]})

        # INSTANCES

        # Instance: Account
        self.invoice_account = self.account_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1)
        # Instance: Invoice Line
        self.invoice_line = self.account_invoice_line.create(
            {'name': 'Test invoice line',
             'account_id': self.invoice_account.id,
             'quantity': 1.000,
             'price_unit': 2.99})

    def test_action_move_create(self):
        # Creation of an invoice instance, wrong check_total
        # Result: UserError
        with self.assertRaises(UserError):
            self.account_invoice.create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'account_id': self.invoice_account.id,
                'type': 'in_invoice',
                'check_total': 1.19,
                'invoice_line_ids': [(6, 0, [self.invoice_line.id])]
            }).action_move_create()
