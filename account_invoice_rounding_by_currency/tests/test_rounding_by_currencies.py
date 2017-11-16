# -*- coding: utf-8 -*-
# Copyright 2015 Alessio Gerace <alessio.gerace@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import workflow
import openerp.tests.common as test_common


class TestRoundingByCurrencies(test_common.SingleTransactionCase):

    def setUp(self):
        super(TestRoundingByCurrencies, self).setUp()
        self.data_model = self.registry('ir.model.data')
        self.invoice_model = self.registry('account.invoice')
        self.context = {}
        self.maxDiff = None
        self.company = self.env.ref('base.main_company')

    def test_0_invoice(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.data_model.get_object_reference(
            cr, uid, 'account_invoice_rounding_by_currency',
            'invtest_invoice_0'
        )
        if invoice_id:
            invoice_id = invoice_id and invoice_id[1] or False
        invoice = self.invoice_model.browse(cr, uid, invoice_id)
        self.assertEqual(invoice.state, 'draft')
        workflow.trg_validate(
            uid, 'account.invoice', invoice_id, 'invoice_open', cr
        )
        self.assertEqual(invoice.state, 'open')
        self.assertEqual(invoice.amount_total, 110.0)

    def test_1_invoice(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.data_model.get_object_reference(
            cr, uid, 'account_invoice_rounding_by_currency',
            'invtest_invoice_1'
        )
        if invoice_id:
            invoice_id = invoice_id and invoice_id[1] or False
        invoice = self.invoice_model.browse(cr, uid, invoice_id)
        self.assertEqual(invoice.state, 'draft')
        workflow.trg_validate(
            uid, 'account.invoice', invoice_id, 'invoice_open', cr
        )
        self.assertEqual(invoice.state, 'open')
        self.assertEqual(invoice.amount_total, 110.45)

    def test_2_invoice(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.data_model.get_object_reference(
            cr, uid, 'account_invoice_rounding_by_currency',
            'invtest_invoice_2'
        )
        if invoice_id:
            invoice_id = invoice_id and invoice_id[1] or False
        invoice = self.invoice_model.browse(cr, uid, invoice_id)
        self.assertEqual(invoice.state, 'draft')
        workflow.trg_validate(
            uid, 'account.invoice', invoice_id, 'invoice_open', cr
        )
        self.assertEqual(invoice.state, 'open')
        self.assertEqual(invoice.amount_total, 110.50)
