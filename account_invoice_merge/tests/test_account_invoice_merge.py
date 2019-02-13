# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


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

        self.invoice_account = self.acc_model.search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1)

        self.invoice_line1 = self._create_inv_line(self.invoice_account.id)
        self.invoice_line2 = self.invoice_line1.copy()
        self.invoice_line3 = self._create_inv_line(self.invoice_account.id)

        self.invoice1 = self._create_invoice(
            self.partner1, 'A', self.invoice_line1)
        self.invoice2 = self._create_invoice(
            self.partner1, 'B', self.invoice_line2)
        self.invoice3 = self._create_invoice(
            self.partner2, 'C', self.invoice_line3)

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

    def _create_invoice(self, partner, name, inv_line):
        invoice = self.inv_model.create({
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
        with self.assertRaises(UserError):
            wiz_id.fields_view_get()

    def test_dirty_check(self):
        """ Check  """
        wiz_id = self.wiz.with_context(
            active_model='account.invoice'
        )

        # Check with only one invoice
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id])\
                .fields_view_get()

        # Check with two different invoice type
        # Create the invoice 4 with a different account
        new_account = self.acc_model.create({
            'code': 'TEST',
            'name': 'Test Account',
            'reconcile': True,
            'user_type_id':
                self.env.ref('account.data_account_type_receivable').id
        })
        invoice_line4 = self._create_inv_line(new_account.id)
        invoice4 = self._create_invoice(self.partner1, 'D', invoice_line4)
        invoice4.account_id = new_account.id
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id, invoice4.id]) \
                .fields_view_get()

        # Check with a canceled invoice
        # Create and cancel the invoice 5
        invoice_line5 = self._create_inv_line(self.invoice_account.id)
        invoice5 = self._create_invoice(self.partner1, 'E', invoice_line5)
        invoice5.action_invoice_cancel()
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id, invoice5.id]) \
                .fields_view_get()

        # Check with an another company
        # Create the invoice 6 and change the company
        invoice_line6 = self._create_inv_line(self.invoice_account.id)
        invoice6 = self._create_invoice(self.partner1, 'E', invoice_line6)
        new_company = self.env['res.company'].create({
            'name': 'Hello World'
        })
        invoice6.company_id = new_company.id
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id, invoice6.id]) \
                .fields_view_get()

        # Check with two different partners
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id, self.invoice3.id]) \
                .fields_view_get()
