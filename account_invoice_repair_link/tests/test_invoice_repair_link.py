# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestAccountInvoiceRepairLink(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceRepairLink, self).setUp()

        self.Repair = self.env['repair.order']
        self.Invoice = self.env['account.invoice']
        self.ResUsers = self.env['res.users']
        self.res_group_user = self.env.ref('stock.group_stock_user')
        self.res_group_manager = self.env.ref('stock.group_stock_manager')

        self.res_repair_user = self.ResUsers.create({
            'name': 'Repair User',
            'login': 'maru',
            'email': 'repair_user@yourcompany.com',
            'groups_id': [(6, 0, [self.res_group_user.id])]})

        self.res_repair_manager = self.ResUsers.create({
            'name': 'Repair Manager',
            'login': 'marm',
            'email': 'repair_manager@yourcompany.com',
            'groups_id': [(6, 0, [self.res_group_manager.id])]})

    def _create_simple_repair_order(self, invoice_method):
        product_to_repair = self.env.ref('product.product_product_5')
        partner = self.env.ref('base.res_partner_address_1')
        return self.env['repair.order'].create({
            'product_id': product_to_repair.id,
            'product_uom': product_to_repair.uom_id.id,
            'address_id': partner.id,
            'guarantee_limit': datetime.today().strftime('%Y-%m-%d'),
            'invoice_method': invoice_method,
            'partner_invoice_id': partner.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'partner_id': self.env.ref('base.res_partner_12').id
        })

    def _create_simple_operation(self, repair_id=False, qty=0.0,
                                 price_unit=0.0):
        product_to_add = self.env.ref('product.product_product_5')
        return self.env['repair.line'].create({
            'name': 'Add The product',
            'type': 'add',
            'product_id': product_to_add.id,
            'product_uom_qty': qty,
            'product_uom': product_to_add.uom_id.id,
            'price_unit': price_unit,
            'repair_id': repair_id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.location_production').id,
        })

    def test_00_invoice_repair_link(self):
        repair = self._create_simple_repair_order('after_repair')
        self._create_simple_operation(repair_id=repair.id, qty=1.0,
                                      price_unit=50.0)
        # Confirm Repair order taking Invoice Method 'After Repair'.
        repair.sudo(self.res_repair_user.id).action_repair_confirm()

        # Check the state is in "Confirmed".
        self.assertEqual(repair.state, "confirmed",
                         'Repair order should be in "Confirmed" state.')
        repair.action_repair_start()

        # Check the state is in "Under Repair".
        self.assertEqual(repair.state, "under_repair",
                         'Repair order should be in "Under_repair" state.')

        # Repairing process for product is in Done state and I end Repair
        # process by clicking on "End Repair" button.
        repair.action_repair_end()

        repair.action_repair_invoice_create()
        # Look for invoice created and check that has a link to the repair
        invoice_id = repair.invoice_id
        self.assertIn(repair.id, invoice_id.repair_ids.ids)
