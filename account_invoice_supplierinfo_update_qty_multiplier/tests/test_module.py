# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.AccountInvoice = self.env['account.invoice']
        self.WizardUpdate = self.env['wizard.update.invoice.supplierinfo']
        self.SupplierInfo = self.env['product.supplierinfo']

        self.product1 = self.env.ref('product.product_product_4b')
        unit = self.env.ref('uom.product_uom_unit')
        account_id = self.env['account.account'].search(
            [('user_type_id.type', '=', 'payable')], limit=1).id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1).id
        product_account_id = self.env.ref(
            'account.demo_coffee_machine_account').id

        self.invoice = self.AccountInvoice.create({
            'journal_id': journal_id,
            'partner_id': self.env.ref('base.res_partner_12').id,
            'account_id': account_id,
            'date_invoice': '%s-01-01' % datetime.now().year,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product1.id,
                'name': 'iPad Retina Display',
                'quantity': 10.0,
                'price_unit': 400.0,
                'uom_id': unit.id,
                'account_id': product_account_id,
            })],
        })

    # Test Section
    def test_wizard(self):
        # Launch and confirm Wizard
        lines_for_update = self.invoice._get_update_supplierinfo_lines()
        wizard = self.WizardUpdate.with_context(
            default_line_ids=lines_for_update,
            default_invoice_id=self.invoice.id).create({})
        wizard.line_ids[0].new_multiplier_qty = 55
        wizard.update_supplierinfo()

        # Check Regressions
        supplierinfo = self.SupplierInfo.search([
            ('product_tmpl_id', '=', self.product1.product_tmpl_id.id),
            ('name', '=', self.invoice.partner_id.id)])

        self.assertEqual(
            len(supplierinfo), 1,
            "Regression : Confirming wizard should have create a supplierinfo")

        self.assertEqual(
            supplierinfo.multiplier_qty, 55,
            "Confirming wizard should have update Multiplier Qty field.")
