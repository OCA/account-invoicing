# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_split,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_split is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_split is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_split.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp import workflow, exceptions


class TestAccountInvoiceSplit(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceSplit, self).setUp()
        self.context = self.env['res.users'].context_get()
        self.split_obj = self.env['account.invoice.split']
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.invoice_01 = self.env.ref('account.demo_invoice_0')

    def test_split_invoice_line_quantity(self):
        line_to_split = self.invoice_01.invoice_line[0]
        line_to_split.quantity = 5
        original_quantity = line_to_split.quantity
        wiz = self.split_obj.with_context(active_ids=[self.invoice_01.id])\
            .create({})
        wiz_line = wiz.line_ids\
            .filtered(lambda r: (r.origin_invoice_line_id == line_to_split))
        quantity_to_split = 1
        wiz_line.quantity_to_split = quantity_to_split
        new_invoice_id = wiz._split_invoice()
        # I check if a new invoice is created
        self.assertTrue(new_invoice_id is not False)
        # I check if there is one and only one line on the created invoice
        new_invoice = self.invoice_obj.browse([new_invoice_id])[0]
        self.assertEqual(len(new_invoice.invoice_line), 1)
        # I check the quantity on the new invoice line
        new_invoice_line = new_invoice.invoice_line[0]
        self.assertEqual(new_invoice_line.quantity, quantity_to_split)
        # I check the remaining quantity on the original invoice
        self.assertEqual(line_to_split.quantity,
                         original_quantity - quantity_to_split)

    def test_split_invoice_line_remove_line(self):
        line_to_split = self.invoice_01.invoice_line[0]
        line_to_split.quantity = 1
        wiz = self.split_obj.with_context(active_ids=[self.invoice_01.id])\
            .create({})
        wiz_line = wiz.line_ids\
            .filtered(lambda r: (r.origin_invoice_line_id == line_to_split))
        quantity_to_split = 1
        wiz_line.quantity_to_split = quantity_to_split
        wiz._split_invoice()
        # I check that the line to split is deleted
        self.assertFalse(line_to_split.exists())

    def test_split_open_invoice(self):
        # I post the created invoice
        workflow.trg_validate(self.uid, 'account.invoice', self.invoice_01.id,
                              'invoice_open', self.cr)
        # Attempt to open the split wizard on an open invoice to check
        # if an exception is raised
        self.assertRaises(
            exceptions.Warning,
            self.split_obj.with_context(active_ids=[self.invoice_01.id])
                .create, {})
