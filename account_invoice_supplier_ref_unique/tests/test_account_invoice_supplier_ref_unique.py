# -*- coding: utf-8 -*-
# Copyright 2016 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.exceptions import ValidationError
from openerp.tests import common


class TestAccountInvoiceSupplierRefUnique(common.TransactionCase):

    def test_check_unique_supplier_invoice_number_insensitive(self):
        invoice_account_id = self.env['account.account'].search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1).id

        # Creation of an invoice instance
        self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'account_id': invoice_account_id,
            'type': 'in_invoice',
            'supplier_invoice_number': 'ABC123'})

        # A new invoice instance with an existing supplier_invoice_number
        with self.assertRaises(ValidationError):
            self.env['account.invoice'].create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'account_id': invoice_account_id,
                'type': 'in_invoice',
                'supplier_invoice_number': 'ABC123'})
