# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo.tests.common import TransactionCase


class Tests(TransactionCase):

    def setUp(self):
        super(Tests, self).setUp()
        self.wizard_obj = self.env['wizard.update.invoice.supplierinfo']
        self.supplierinfo_obj = self.env['product.supplierinfo']
        self.invoice_model = self.env['account.invoice']
        journal_model = self.env['account.journal']
        self.journal = journal_model.search(
            [('type', '=', 'sale')], limit=1)
        self.product = self.env.ref('product.product_product_4b')
        self.prod_account = self.env.ref('account.demo_coffee_machine_account')

        self.invoice = self.invoice_model.create(
            {'journal_id': self.journal.id,
             'partner_id': self.env.ref('base.res_partner_12').id,
             'account_id':
             self.env['account.account'].
             search([('user_type_id.type', '=', 'payable')], limit=1).id,
             'date_invoice': '%s-01-01' % datetime.now().year,
             'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                          'name': 'iPad Retina Display',
                                          'quantity': 10.0,
                                          'price_unit': 400.0,
                                          'account_id': self.prod_account.id,
                                          })],
             })

    def test_with_update_pricelist_supplierinfo_on_product_template(self):
        # supplier invoice with pricelist supplierinfo to update and
        # product supplierinfo is on product_template

        vals_wizard = self.invoice.check_supplierinfo().get('context', {})

        line_ids = vals_wizard.get('default_line_ids', {})
        invoice_id = vals_wizard.get('default_invoice_id', {})

        self.assertEquals(len(line_ids), 1)
        self.assertEquals(line_ids[0][2]['current_price'], False)
        self.assertEquals(line_ids[0][2]['new_price'], 400.0)

        # Create and launch update process
        wizard = self.wizard_obj.create({
            'line_ids': line_ids,
            'invoice_id': invoice_id,
        })
        wizard.update_supplierinfo()

        supplierinfos = self.supplierinfo_obj.search([
            ('name', '=', self.invoice.supplier_partner_id.id),
            (
                'product_tmpl_id', '=',
                self.invoice.invoice_line_ids[0].
                product_id.product_tmpl_id.id),
        ])
        self.assertEquals(len(supplierinfos), 1)

        self.assertEquals(supplierinfos.price, 400.0)
