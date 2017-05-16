# -*- coding: utf-8 -*-
# Copyright 2016 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields
from openerp.exceptions import ValidationError
from openerp.tests.common import SavepointCase


class TestAccountInvoiceSupplierRefUnique(SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestAccountInvoiceSupplierRefUnique, self).setUpClass()

        # ENVIRONMENTS
        self.account_account = self.env['account.account']
        self.account_invoice = self.env['account.invoice']
        self.account_invoice_line = self.env['account.invoice.line']

        # INSTANCES
        self.partner = self.env.ref('base.res_partner_2')
        # Account for invoice
        self.account = self.account_account.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1)
        self.account_expenses = self.account_account.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_expenses').id)], limit=1)
        # Invoice with unique reference 'ABC123'
        self.invoice = self.account_invoice.create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
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

    def test_refund_with_unique_supplier_invoice_number(self):
        self.account_invoice_line.create({
            'invoice_id': self.invoice.id,
            'product_qty': 1.00,
            'price_unit': 1.00,
            'name': "Invoice line 1",
            'account_id': self.account_expenses.id,
        })
        self.invoice.signal_workflow('invoice_open')

        invoice_refund_model = self.env['account.invoice.refund']
        invoice_refund_model = invoice_refund_model.with_context(
            active_ids=[self.invoice.id])

        account_invoice_refund = invoice_refund_model.create({
            'description': "Refund test",
            'date': fields.Date.today(),
            'filter_refund': 'refund',
            'supplier_invoice_number': "321CBA"
        })

        # I clicked on refund button.
        res = account_invoice_refund.invoice_refund()
        credit_note_id = res['domain'][1][2][0]
        credit_note = self.account_invoice.browse(credit_note_id)
        self.assertEqual(credit_note.type, 'in_refund')
        self.assertEqual(credit_note.supplier_invoice_number, '321CBA')
