# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Agile Business Group (<http://www.agilebg.com>)
#    Author: Alessio Gerace <alessio.gerace@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
