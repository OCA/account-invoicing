# -*- coding: utf-8 -*-
# © 2011 Domsense s.r.l. (<http://www.domsense.com>).
# © 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# © 2015 ACSONE SA/NV (<http://acsone.eu>)
# © 2016 Farid Shahy (<fshahy@gmail.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestAccountInvoiceShippement(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceShippement, self).setUp()
        self.inv_model = self.env['account.invoice']
        self.stock_model = self.env['stock.picking']

        self.partner_2 = self.ref('base.res_partner_2')
        self.partner_address_3 = self.ref('base.res_partner_address_3')
        self.shipment4 = self.ref('stock.incomming_shipment4')
        self.account_journal = self.ref('account.check_journal')

    def test_create_invoice_from_stock(self):
        stock = self.stock_model.browse(self.shipment4)

        stock.invoice_state = '2binvoiced'
        stock.partner_id = self.partner_address_3
        stock.move_lines[0].partner_id = self.partner_2

        res = stock.action_invoice_create(journal_id=self.account_journal)
        self.assertEqual(len(res), 1)
        inv_id = res[0]

        created_invoice = self.inv_model.browse(inv_id)

        self.assertEqual(created_invoice.partner_id.id,
                         self.partner_address_3)
        self.assertEqual(created_invoice.address_shipping_id.id,
                         self.partner_2)
