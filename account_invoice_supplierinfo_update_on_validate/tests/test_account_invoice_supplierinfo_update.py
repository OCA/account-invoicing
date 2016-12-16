# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class Tests(TransactionCase):

    def setUp(self):
        super(Tests, self).setUp()
        self.wizard_obj = self.env['wizard.update.invoice.supplierinfo']
        self.supplierinfo_obj = self.env['product.supplierinfo']
        self.partnerinfo_obj = self.env['pricelist.partnerinfo']
        self.invoice = self.env.ref(
            'account_invoice_supplierinfo_update_on_validate.'
            'account_invoice_6')

    def test_validate_without_update_pricelist_supplierinfo_product_template(
            self):
        # supplier invoice with pricelist supplierinfo to update and
        # product supplierinfo is on product_template
        vals_wizard = self.invoice.check_supplierinfo().get('context', {})

        line_ids = vals_wizard.get('default_line_ids', {})
        invoice_id = vals_wizard.get('default_invoice_id', {})
        self.assertEquals(len(line_ids), 1)
        self.assertEquals(line_ids[0][2]['current_price'], False)
        self.assertEquals(line_ids[0][2]['new_price'], 400.0)

        wizard = self.wizard_obj.create({
            'line_ids': line_ids,
            'invoice_id': invoice_id,
        })
        # validate invoice without update supplierinfo
        wizard.with_context(
            active_id=wizard.invoice_id.id).set_supplierinfo_ok()

        self.assertEquals(self.invoice.state, 'open')
        self.assertEquals(self.invoice.supplierinfo_ok, True)

        supplierinfos = self.supplierinfo_obj.search([
            ('name', '=', self.invoice.supplier_partner_id.id),
            (
                'product_tmpl_id', '=',
                self.invoice.invoice_line[0].product_id.product_tmpl_id.id),
        ])
        self.assertEquals(len(supplierinfos), 0)
