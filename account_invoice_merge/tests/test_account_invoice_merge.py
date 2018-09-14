# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2018 Valentin Vinagre <valentin.vinagre@qubiq.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase
from odoo.exceptions import Warning


class TestAccountInvoiceMerge(TransactionCase):
    """
        Tests for Account Invoice Merge.
    """
    def setUp(self):
        super(TestAccountInvoiceMerge, self).setUp()
        self.par_model = self.env['res.partner']
        self.context = self.env['res.users'].context_get()
        self.acc_model = self.env['account.account']
        self.inv_model = self.env['account.invoice']
        self.inv_line_model = self.env['account.invoice.line']
        self.wiz = self.env['invoice.merge']

        self.partner1 = self._create_partner()
        self.partner2 = self._create_partner()
        self.partner3 = self._create_partner()
        self.partner4 = self._create_partner()

        self.invoice_account = self.acc_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1)

        self.invoice_account2 = self.acc_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_payable').id
              )], limit=1)

        self.invoice_line1 = self._create_inv_line(self.invoice_account.id)
        self.invoice_line2 = self.invoice_line1.copy()
        self.invoice_line3 = self._create_inv_line(self.invoice_account.id)
        self.invoice_line4_1 = self._create_inv_line(self.invoice_account.id)
        self.invoice_line4_1.write({
            'name': 'test invoice line dif',
            'quantity': 3.0,
            'price_unit': 4.0,
            })
        self.invoice_line4_2 = self.invoice_line1.copy()
        self.invoice_line5 = self.invoice_line1.copy()
        self.invoice_line6 = self._create_inv_line(self.invoice_account2.id)
        self.invoice_line7 = self.invoice_line1.copy()
        self.invoice_line8 = self.invoice_line1.copy()
        self.invoice_line9 = self.invoice_line1.copy()

        self.invoice1 = self._create_invoice(
            self.partner1, 'A', [self.invoice_line1.id, ])
        self.invoice2 = self._create_invoice(
            self.partner1, 'B', [self.invoice_line2.id, ])
        self.invoice3 = self._create_invoice(
            self.partner2, 'C', [self.invoice_line3.id, ])
        self.invoice4 = self._create_invoice(
            self.partner3, 'D',
            [self.invoice_line4_1.id, self.invoice_line4_2.id])
        self.invoice5 = self._create_invoice(
            self.partner3, 'E', [self.invoice_line5.id, ])
        self.invoice6 = self._create_invoice(
            self.partner1, 'F', [self.invoice_line6.id, ])
        self.invoice6.account_id = self.env['account.account'].search([
            ('id', '!=', self.invoice1.account_id.id)
            ])[3].id
        self.invoice7 = self._create_invoice(
            self.partner4, 'G', [self.invoice_line7.id, ])
        self.invoice7.type = 'out_refund'
        self.invoice8 = self._create_invoice(
            self.partner4, 'H', [self.invoice_line8.id, ])
        self.invoice9 = self._create_invoice(
            self.partner4, 'I', [self.invoice_line9.id, ])
        self.invoice9.journal_id = self.env['account.journal'].search([
            ('id', '!=', self.invoice7.journal_id.id)
            ])[1].id

    def _create_partner(self):
        partner = self.par_model.create({
            'name': 'Test Partner',
            'supplier': True,
            'company_type': 'company',
        })
        return partner

    def _create_inv_line(self, account_id):
        inv_line = self.inv_line_model.create({
            'name': 'test invoice line',
            'account_id': account_id,
            'quantity': 1.0,
            'price_unit': 3.0,
            'product_id': self.env.ref('product.product_product_8').id
        })
        return inv_line

    def _create_invoice(self, partner, name, inv_lines):
        invoice = self.inv_model.create({
            'partner_id': partner.id,
            'name': name,
            'invoice_line_ids':
            [(4, x, None) for x in inv_lines],
        })
        return invoice

    def test_account_invoice_merge_1(self):
        self.assertEqual(len(self.invoice1.invoice_line_ids), 1)
        self.assertEqual(len(self.invoice2.invoice_line_ids), 1)
        start_inv = self.inv_model.search(
            [('state', '=', 'draft'), ('partner_id', '=', self.partner1.id)])
        self.assertEqual(len(start_inv), 3)
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

        end_inv = self.inv_model.search([
            ('state', '=', 'draft'),
            ('partner_id', '=', self.partner1.id)
            ], order="id desc")
        self.assertEqual(len(end_inv), 2)
        self.assertEqual(len(end_inv[0].invoice_line_ids), 1)
        self.assertEqual(end_inv[0].invoice_line_ids[0].quantity, 2.0)

    # error partner_id
    def test_account_invoice_merge_2(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice3.id],
            active_model='account.invoice'
        ).create({})
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()

    # error account
    def test_account_invoice_merge_2_1(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice6.id],
            active_model='account.invoice'
        ).create({})
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()

    # error active_ids
    def test_account_invoice_merge_2_2(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id],
            active_model='account.invoice'
        ).create({})
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()

    # error type
    def test_account_invoice_merger_2_3(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice7.id],
            active_model='account.invoice'
        ).create({})
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()

    # error journal_id
    def test_account_invoice_merger_2_4(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice7.id, self.invoice9.id],
            active_model='account.invoice'
        ).create({})
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()

    # error state
    def test_account_invoice_merge_2_6(self):
        self.invoice3.action_invoice_open()
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice3.id],
            active_model='account.invoice'
        ).create({})
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()

    def test_account_invoice_merge_3(self):
        self.assertEqual(len(self.invoice4.invoice_line_ids), 2)
        self.assertEqual(len(self.invoice5.invoice_line_ids), 1)
        start_inv = self.inv_model.search(
            [('state', '=', 'draft'), ('partner_id', '=', self.partner3.id)])
        self.assertEqual(len(start_inv), 2)
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice4.id, self.invoice5.id],
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
        cancel_inv = self.inv_model.search(
            [('state', '=', 'cancel'), ('partner_id', '=', self.partner3.id)])
        self.assertEqual(len(cancel_inv), 2)
        end_inv = self.inv_model.search(
            [('state', '=', 'draft'),
             ('partner_id', '=', self.partner3.id)])
        self.assertEqual(len(end_inv), 1)
        self.assertEqual(len(end_inv[0].invoice_line_ids), 2)

        self.assertEqual(end_inv[0].invoice_line_ids.filtered(
            lambda x: x.name != 'test invoice line dif')[0].quantity, 2.0)
        self.assertEqual(end_inv[0].invoice_line_ids.filtered(
            lambda x: x.name == 'test invoice line dif')[0].quantity, 3.0)
