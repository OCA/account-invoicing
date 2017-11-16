# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError


class TestAccountInvoiceMerge(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceMerge, self).setUp()

        self.wiz_model = self.env['invoice.merge']
        self.wiz_context = {'active_model': 'account.invoice'}
        self.invoice_model = self.env['account.invoice']
        self.account_payable = self.env.ref('account.a_pay')
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_2 = self.env.ref('base.res_partner_2')

        self.supplier_invoice_1 = self.invoice_model.create(
            {'journal_id': self.env.ref('account.expenses_journal').id,
             'type': 'in_invoice',
             'partner_id': self.partner_1.id,
             'account_id': self.account_payable.id,
             'invoice_line': [(0, 0, {'name': 'Inv 1 - Line 1',
                                      'price_unit': 100.0})],
             })

        self.supplier_invoice_2 = self.invoice_model.create(
            {'journal_id': self.env.ref('account.expenses_journal').id,
             'type': 'in_invoice',
             'partner_id': self.partner_1.id,
             'account_id': self.account_payable.id,
             'invoice_line': [(0, 0, {'name': 'Inv 2 - Line 1',
                                      'price_unit': 150.0})],
             })

        self.supplier_invoice_3 = self.invoice_model.create(
            {'journal_id': self.env.ref('account.expenses_journal').id,
             'type': 'in_invoice',
             'partner_id': self.partner_2.id,
             'account_id': self.account_payable.id,
             'invoice_line': [(0, 0, {'name': 'Inv 3 - Line 1',
                                      'price_unit': 50.0})],
             })

    def test_invoice_merge(self):
        invoices = self.supplier_invoice_1 + self.supplier_invoice_2
        invoices_info, invoice_lines_info = invoices.do_merge()
        for k in invoices_info:
            new_inv = self.invoice_model.browse(k)
            self.assertEqual(new_inv.amount_total, 250.0)
            new_inv_line_ids = invoice_lines_info[k].values()
            self.assertEqual(
                len(new_inv_line_ids), len(new_inv.invoice_line._ids),
                "Incorrect Invoice Line Mapping")

    def test_invoice_merge_wizard(self):
        invoices = self.supplier_invoice_1 + self.supplier_invoice_2
        ctx = dict(self.wiz_context, active_ids=invoices._ids)
        wiz = self.wiz_model.with_context(ctx).create({})
        act = wiz.merge_invoices()
        self.assertEqual(
            len(act['domain'][0][2]), 3, "Error in invoice.merge wizard")

    def test_dirty_check(self):
        invoices = self.supplier_invoice_1 + self.supplier_invoice_3
        ctx = dict(self.wiz_context, active_ids=invoices._ids)
        wiz = self.wiz_model.with_context(ctx).create({})
        with self.assertRaises(UserError):
            wiz._dirty_check()
