# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SavepointCase
from odoo.exceptions import Warning


class TestAccountInvoiceMerge(SavepointCase):
    """Tests for Account Invoice Merge.
    """
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceMerge, cls).setUpClass()
        cls.par_model = cls.env['res.partner']
        cls.context = cls.env['res.users'].context_get()
        cls.acc_model = cls.env['account.account']
        cls.inv_model = cls.env['account.invoice']
        cls.inv_line_model = cls.env['account.invoice.line']
        cls.wiz = cls.env['invoice.merge']

        cls.partner1 = cls._create_partner()
        cls.partner2 = cls._create_partner()

        cls.invoice_account = cls.acc_model.search(
            [('user_type_id',
              '=',
              cls.env.ref('account.data_account_type_receivable').id
              )], limit=1)

        cls.invoice_line1 = cls._create_inv_line(cls.invoice_account.id)
        cls.invoice_line2 = cls.invoice_line1.copy()
        cls.invoice_line3 = cls._create_inv_line(cls.invoice_account.id)

        cls.invoice1 = cls._create_invoice(
            cls.partner1, 'A', cls.invoice_line1)
        cls.invoice2 = cls._create_invoice(
            cls.partner1, 'B', cls.invoice_line2)
        cls.invoice3 = cls._create_invoice(
            cls.partner2, 'C', cls.invoice_line3)

    @classmethod
    def _create_partner(cls):
        partner = cls.par_model.create({
            'name': 'Test Partner',
            'supplier': True,
            'company_type': 'company',
        })
        return partner

    @classmethod
    def _create_inv_line(cls, account_id):
        inv_line = cls.inv_line_model.create({
            'name': 'test invoice line',
            'account_id': account_id,
            'quantity': 1.0,
            'price_unit': 3.0,
            'product_id': cls.env.ref('product.product_product_8').id
        })
        return inv_line

    @classmethod
    def _create_invoice(cls, partner, name, inv_line):
        invoice = cls.inv_model.create({
            'partner_id': partner.id,
            'name': name,
            'invoice_line_ids': [(4, inv_line.id)],
        })
        return invoice

    def test_account_invoice_merge_1(self):
        self.assertEqual(len(self.invoice1.invoice_line_ids), 1)
        self.assertEqual(len(self.invoice2.invoice_line_ids), 1)
        start_inv = self.inv_model.search(
            [('state', '=', 'draft'), ('partner_id', '=', self.partner1.id)])
        self.assertEqual(len(start_inv), 2)

        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice2.id],
            active_model='account.invoice'
        ).create({})
        wiz_id.fields_view_get()
        action = wiz_id.merge_invoices()

        self.assertDictContainsSubset(
            {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'xml_id': 'account.action_invoice_tree1',
            },
            action,
            'There was an error and the two invoices were not merged.'
        )

        end_inv = self.inv_model.search(
            [('state', '=', 'draft'),
             ('partner_id', '=', self.partner1.id)])
        self.assertEqual(len(end_inv), 1)
        self.assertEqual(len(end_inv[0].invoice_line_ids), 1)
        self.assertEqual(end_inv[0].invoice_line_ids[0].quantity, 2.0)

    def test_account_invoice_merge_2(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice3.id],
            active_model='account.invoice'
        ).create({})
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()
