# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestUpdateSupplierPrice(TransactionCase):
    def test_with_update_pricelist_supplierinfo_on_product_template(self):
        # supplier invoice with pricelist supplierinfo to update and
        # product supplierinfo is on product_template
        invoice_6 = self.env.ref(
            'account_invoice_product_supplier_price_update.account_invoice_6')
        result6 = invoice_6.invoice_open()
        # open new form when pricelist supplierinfo to update
        self.assertEquals(result6['view_mode'], 'form')
        self.assertEquals(result6['res_model'], 'update.supplierprice')
        self.assertEquals(len(result6['context']['default_wizard_line_ids']),
                          1)
        self.assertEquals(result6['context']['default_wizard_line_ids'][0][2]
                          ['current_price_unit'], False)
        self.assertEquals(result6['context']['default_wizard_line_ids']
                          [0][2]['new_price_unit'], 400.0)
        self.assertEquals(result6['type'], 'ir.actions.act_window')
        self.assertEquals(result6['target'], 'new')
        (result6['context']['default_wizard_line_ids'][0][2]
         ['to_variant']) = False
        vals = {
            'wizard_line_ids': result6['context']['default_wizard_line_ids'],
        }
        wizard = (self.env['update.supplierprice'].
                  create(vals))
        # add pricelist partnerinfo
        (wizard.with_context(active_id=invoice_6.id).
         update_product_supplierprice())
        for line in wizard.wizard_line_ids:
            pricelist_partnerinfos = self.env['pricelist.partnerinfo'].search([
                ('suppinfo_id', '=', line.suppinfo_id.id),
                ('min_quantity', '=', 0.0),
                ('price', '=', line.new_price_unit)
            ])
            self.assertNotEquals(pricelist_partnerinfos, False)

    def test_with_update_pricelist_supplierinfo_on_product_product(self):
        # supplier invoice with pricelist supplierinfo to update and
        # product supplierinfo is on product_product
        invoice_7 = self.env.ref(
            'account_invoice_product_supplier_price_update.account_invoice_7')
        result7 = invoice_7.invoice_open()
        # open new form when pricelist supplierinfo to update
        self.assertEquals(result7['view_mode'], 'form')
        self.assertEquals(result7['res_model'], 'update.supplierprice')
        self.assertEquals(len(result7['context']['default_wizard_line_ids']),
                          1)
        self.assertEquals(result7['context']['default_wizard_line_ids'][0][2]
                          ['current_price_unit'], False)
        self.assertEquals(result7['context']['default_wizard_line_ids']
                          [0][2]['new_price_unit'], 1000.0)
        self.assertEquals(result7['type'], 'ir.actions.act_window')
        self.assertEquals(result7['target'], 'new')
        vals = {
            'wizard_line_ids': result7['context']['default_wizard_line_ids'],
        }
        wizard = self.env['update.supplierprice'].create(vals)
        # add pricelist partnerinfo
        (wizard.with_context(active_id=invoice_7.id).
         update_product_supplierprice())
        for line in wizard.wizard_line_ids:
            pricelist_partnerinfos = self.env['pricelist.partnerinfo'].search([
                ('suppinfo_id', '=', line.suppinfo_id.id),
                ('min_quantity', '=', 0.0),
                ('price', '=', line.new_price_unit)
            ])
            self.assertNotEquals(pricelist_partnerinfos, False)

    def test_without_update_pricelist_supplierinfo(self):
        # supplier invoice without pricelist supplierinfo to update
        invoice_8 = self.env.ref(
            'account_invoice_product_supplier_price_update.account_invoice_8')
        result8 = invoice_8.invoice_open()
        self.assertEquals(result8, None)
