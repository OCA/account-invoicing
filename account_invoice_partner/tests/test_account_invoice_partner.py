# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountInvoiceParner(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceParner, cls).setUpClass()

        # MODELS
        cls.inv_model = cls.env['account.invoice']
        cls.partner_model = cls.env['res.partner']

        # INSTANCE
        # partners
        partners = cls.partner_model.search([
            ('type', '!=', 'invoice'),
            ('child_ids', '=', False)
        ])
        cls.partner = partners[0]
        cls.partner_2 = partners[1]

        # invoice
        account_payable = cls.env['account.account'].create(
            {'code': 'X1111', 'name': 'Sale - Test Payable Account',
             'user_type_id': cls.env.ref(
                 'account.data_account_type_payable').id,
             'reconcile': True
             })
        journal = cls.env['account.journal'].create(
            {'name': 'Purchase Journal - Test',
             'code': 'STPJ',
             'type': 'purchase'
             })
        invoice_vals = {
            'name': 'TEST',
            'type': 'in_invoice',
            'partner_id': cls.partner.id,
            'account_id': account_payable.id,
            'journal_id': journal.id,
        }
        cls.invoice = cls.env['account.invoice'].create(invoice_vals)

    def test_0(self):
        # these partners are differents
        self.assertNotEqual(self.partner, self.partner_2)

        # partner is define in invoice
        self.assertEqual(self.invoice.partner_id, self.partner)

        # partner has no address defined for invoice
        res = self.invoice._onchange_partner_id()
        self.assertFalse('value' in res)

        # change partner type to define partner invoice address
        self.partner_2.write({'type': 'invoice'})
        self.partner.write({'child_ids': [(6, 0, self.partner_2.ids)]})
        data = self.partner._convert_to_write(self.partner._cache)
        self.assertEqual(data['child_ids'], [(6, 0, self.partner_2.ids)])

        # test onchange function
        res = self.invoice._onchange_partner_id()
        self.assertEqual(self.invoice.partner_id.id, self.partner_2.id)
