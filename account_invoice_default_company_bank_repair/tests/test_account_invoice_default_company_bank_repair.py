# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp.tests import common
from openerp import workflow


class TestRepairInvoice(common.TransactionCase):

    def setUp(self):
        super(TestRepairInvoice, self).setUp()
        self.year = datetime.now().year
        self.bank = self.env['res.partner.bank'].create({
            'state': 'bank',
            'acc_number': 12345678901234,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'customer': True,
            'default_company_bank_id': self.bank.id
        })
        self.account = self.env['account.account'].search(
            [('type', '=', 'receivable'), ('currency_id', '=', False)],
            limit=1)[0]
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.list0 = self.ref('product.list0')
        product = self.env['product.product']
        self.product_test = product.create({
            'name': 'Test Product',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'lst_price': 11.55})
        self.location_id = self.env.ref(
            'stock.stock_location_suppliers')
        self.location_dest_id = self.env.ref(
            'stock.stock_location_stock')

    def test_invoice_default_company_bank_repair(self):
        self.repair = self.env['mrp.repair'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'product_qty': 2.00,
            'product_id': self.product_test.id,
            'product_uom': self.uom_unit.id,
            'location_id': self.location_id.id,
            'invoice_method': 'b4repair',
            'location_dest_id': self.location_dest_id.id,
        })
        workflow.trg_validate(
            self.uid, 'mrp.repair', self.repair.id,
            'repair_confirm', self.cr)
# Create invoice from repair order
        workflow.trg_validate(
            self.uid, 'mrp.repair', self.repair.id,
            'action_invoice_create', self.cr)
        repair_invoice = self.env['account.invoice'].search(
            [('origin', '=', self.repair.name)])
# Compare account number of invoice and partner
        self.assertEqual(
            repair_invoice.partner_bank_id.acc_number,
            self.partner.default_company_bank_id.acc_number)
