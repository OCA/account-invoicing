# Copyright (C) 2020-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPickingInvoicing(TransactionCase):

    def setUp(self):
        super(TestPickingInvoicing, self).setUp()
        self.invoice_wizard = self.env['stock.invoice.onshipping']
        self.invoice_model = self.env['account.invoice']
        self.purchase_model = self.env['purchase.order']
        self.product_model = self.env['product.product']
        self.supplier = self.env.ref('base.res_partner_12')
        self.product_tmpl_model = self.env['product.template']
        self.account_user_type = self.env.ref(
            'account.data_account_type_revenue')
        self.account_revenue = self.env['account.account'].search(
            [('user_type_id', '=',
              self.account_user_type.id)],
            limit=1)
        self.tax_model = self.env['account.tax']
        self.tax_sale_1 = self.tax_model.create({
            'name': 'Sale tax 20',
            'type_tax_use': 'sale',
            'amount': '20.00',
        })
        self.tax_sale_2 = self.tax_model.create({
            'name': 'Sale tax 10',
            'type_tax_use': 'sale',
            'amount': '10.00',
        })
        self.tax_purchase_1 = self.tax_model.create({
            'name': 'Purchase tax 10',
            'type_tax_use': 'purchase',
            'amount': '10.00',
        })
        self.tax_purchase_2 = self.tax_model.create({
            'name': 'Purchase tax 20',
            'type_tax_use': 'purchase',
            'amount': '20.00',
        })
        product_tmpl_1 = self.product_tmpl_model.create({
            'name': 'Test 1',
            'lst_price': '15000',
            'taxes_id': [(6, 0, [self.tax_sale_1.id, self.tax_sale_2.id])],
            'supplier_taxes_id': [
                (6, 0, [self.tax_purchase_1.id, self.tax_purchase_2.id])],
            'property_account_income_id': self.account_revenue.id,

        })
        self.product_test_1 = self.product_model.create({
            'product_tmpl_id': product_tmpl_1.id,
            'standard_price': '500',
        })
        product_tmpl_2 = self.product_tmpl_model.create({
            'name': 'Test 2',
            'lst_price': '15000',
            'taxes_id': [(6, 0, [self.tax_sale_1.id, self.tax_sale_2.id])],
            'supplier_taxes_id': [
                (6, 0, [self.tax_purchase_1.id, self.tax_purchase_2.id])],
            'property_account_income_id': self.account_revenue.id,

        })
        self.product_test_2 = self.product_model.create({
            'product_tmpl_id': product_tmpl_2.id,
            'standard_price': '500',
        })

    def test_supplier_picking_invoicing_purchase(self):
        '''
         Test invoicing picking in to check if get the data
         from purchase order line.
        '''
        nb_invoice_before = self.invoice_model.search_count([])
        po = self.purchase_model.create({
            'partner_id': self.supplier.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_test_1.id,
                    'name': self.product_test_1.name,
                    'product_qty': 3,
                    'price_unit': 100,
                    'product_uom': self.product_test_1.uom_id.id,
                    'date_planned': '2020-05-12',
                }),
                (0, 0, {
                    'product_id': self.product_test_1.id,
                    'name': self.product_test_1.name,
                    'product_qty': 5,
                    'price_unit': 200,
                    'product_uom': self.product_test_1.uom_id.id,
                    'date_planned': '2020-06-12',
                }),
                (0, 0, {
                    'product_id': self.product_test_2.id,
                    'name': self.product_test_2.name,
                    'product_qty': 5,
                    'price_unit': 220,
                    'product_uom': self.product_test_2.uom_id.id,
                    'date_planned': '2020-06-12',
                }),
            ],
        })
        po.button_confirm()
        picking = po.mapped('picking_ids')
        new_move = picking.mapped('move_ids_without_package')
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [('picking_ids', '=', picking.id)]
        invoice = self.invoice_model.search(domain)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(invoice.partner_id, self.supplier)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before, nb_invoice_after - len(invoice))
        assert invoice.invoice_line_ids, 'Error to create invoice line.'
        for po_line in po.order_line:
            self.assertIn(
                po_line, invoice.mapped('invoice_line_ids.purchase_line_id'))
        for inv_line in invoice.invoice_line_ids:
            for po_line in po.order_line:
                if inv_line.purchase_line_id == po_line:
                    self.assertEquals(
                        inv_line.price_unit, po_line.price_unit
                    )
                    self.assertEquals(
                        inv_line.discount, po_line.discount
                    )
                    self.assertEquals(
                        inv_line.uom_id, po_line.product_uom
                    )
            for mv_line in inv_line.move_line_ids:
                self.assertIn(
                    mv_line, new_move,
                    'Error to link stock.move with invoice.line.')
            self.assertTrue(
                inv_line.invoice_line_tax_ids,
                'Error to map Purchase Tax in invoice.line.')
