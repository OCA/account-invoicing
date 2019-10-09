# Copyright 2016 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestAccountInvoiceSupplierRefUnique(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceSupplierRefUnique, cls).setUpClass()

        # ENVIRONMENTS
        cls.account_account = cls.env['account.account']
        cls.account_invoice = cls.env['account.invoice'].with_context(
            {'tracking_disable': True})

        # INSTANCES
        cls.partner = cls.env.ref('base.res_partner_2')
        # Account for invoice
        cls.account = cls.account_account.search(
            [('user_type_id',
              '=',
              cls.env.ref('account.data_account_type_receivable').id
              )], limit=1)
        # Invoice with unique reference 'ABC123'
        cls.invoice = cls.account_invoice.create({
            'partner_id': cls.partner.id,
            'account_id': cls.account.id,
            'type': 'in_invoice',
            'supplier_invoice_number': 'ABC123'})

    def test_check_unique_supplier_invoice_number_insensitive(self):
        # A new invoice instance with an existing supplier_invoice_number
        with self.assertRaises(ValidationError):
            self.account_invoice.create({
                'partner_id': self.partner.id,
                'account_id': self.account.id,
                'type': 'in_invoice',
                'supplier_invoice_number': 'ABC123'})
        # A new invoice instance with a new supplier_invoice_number
        self.account_invoice.create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'type': 'in_invoice',
            'supplier_invoice_number': 'ABC123bis'})

    def test_onchange_supplier_invoice_number(self):
        self.invoice._onchange_supplier_invoice_number()
        self.assertEqual(self.invoice.reference,
                         self.invoice.supplier_invoice_number,
                         "_onchange_supplier_invoice_number")
