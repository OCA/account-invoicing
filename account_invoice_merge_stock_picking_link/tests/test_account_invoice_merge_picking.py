# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.stock.tests.common import TestStockCommon


class TestAccountInvoiceMergePicking(TestStockCommon):

    def setUp(self):
        super(TestAccountInvoiceMergePicking, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        self.picking_x = self.PickingObj.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_in,
            'invoice_state': '2binvoiced'})
        self.move_a1 = self.MoveObj.create({
            'name': self.productA.name,
            'product_id': self.productA.id,
            'product_uom_qty': 1,
            'product_uom': self.productA.uom_id.id,
            'picking_id': self.picking_x.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced'})
        self.move_b = self.MoveObj.create({
            'name': self.productB.name,
            'product_id': self.productB.id,
            'product_uom_qty': 1,
            'product_uom': self.productB.uom_id.id,
            'picking_id': self.picking_x.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced',
        })
        self.picking_y = self.PickingObj.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_in,
            'invoice_state': '2binvoiced'})
        self.move_a2 = self.MoveObj.create({
            'name': self.productA.name,
            'product_id': self.productA.id,
            'product_uom_qty': 5,
            'product_uom': self.productA.uom_id.id,
            'picking_id': self.picking_y.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced'})
        self.res = {}
        self.res[(self.productA.id, self.picking_x.name)] = \
            set([self.move_a1.id])
        self.res[(self.productA.id, self.picking_y.name)] = \
            set([self.move_a2.id])
        self.res[(self.productB.id, self.picking_x.name)] = \
            set([self.move_b.id])

    def _invoice_create(self, picking):
        context = {"active_model": 'stock.picking',
                   "active_ids": [picking.id],
                   "active_id": picking.id}
        wizard = self.env['stock.invoice.onshipping'].with_context(
            context).create({})
        wizard.open_invoice()
        return picking.invoice_id

    def test_invoice_merge(self):
        invoice_a = self._invoice_create(self.picking_x)
        invoice_b = self._invoice_create(self.picking_y)

        # Merge invoices
        context = {"active_ids": [invoice_a.id, invoice_b.id]}
        self.merge_wizard = self.env['invoice.merge'].with_context(
            context).create({})
        action = self.merge_wizard.merge_invoices()
        newid = action['domain'][0][2][-1]
        invoice = self.env['account.invoice'].browse(newid)
        # Check pickings
        self.assertEqual(
            set(invoice.picking_ids.ids),
            set([self.picking_x.id, self.picking_y.id]))
        # Check move lines
        for line in invoice.invoice_line:
            self.assertEqual(
                set(line.move_line_ids.ids),
                self.res[(line.product_id.id, line.origin)])
