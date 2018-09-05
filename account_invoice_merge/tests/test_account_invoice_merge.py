##############################################################################
#
#    Copyright 2004-2010 Tiny SPRL (http://tiny.be).
#    Copyright 2010-2011 Elico Corp.
#    Copyright 2016 Acsone (https://www.acsone.eu/)
#    Copyright 2017 Eficent Business and IT Consulting Services S.L. (http://www.eficent.com)
#    2010-2018 OmniaSolutions (<http://www.omniasolutions.eu>).
#    OmniaSolutions, Open Source Management Solution
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
#
##############################################################################

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
        with self.assertRaises(Warning):
            wiz_id.fields_view_get()
