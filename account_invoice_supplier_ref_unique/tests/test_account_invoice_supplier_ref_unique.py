# -*- coding: utf-8 -*-
# Copyright 2015 Akretion
# Copyright 2010 - 2014 Savoir-Faire-Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.account.tests.account_test_classes\
    import AccountingTestCase
from openerp.exceptions import ValidationError


class TestAccountInvoiceSupplierRefUnique(AccountingTestCase):

    def test_check_unique_supplier_invoice_number_insensitive(self):
        invoice_account = self.env['account.account'].search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1).id

        # Creation of an invoice instance
        self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'account_id': invoice_account,
            'type': 'in_invoice',
            'supplier_invoice_number': 'ABC123'})

        # A new invoice instance with an existing supplier_invoice_number
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env['account.invoice'].create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'account_id': invoice_account,
                'type': 'in_invoice',
                'supplier_invoice_number': 'ABC123'})
